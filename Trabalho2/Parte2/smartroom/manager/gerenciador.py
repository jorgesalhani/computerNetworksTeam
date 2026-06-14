"""Gerenciador TCP do protocolo SMARTROOM/1.0.

Este primeiro bloco funcional aceita conexoes, registra componentes por
HELLO/ACK e mantem o socket aberto para mensagens futuras do protocolo.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from smartroom.protocol.constants import (  # noqa: E402
    ACT_AC_ID,
    ACT_LIGHT_ID,
    ACT_PROJECTOR_ID,
    DEFAULT_ABSENCE_TIMEOUT_SECONDS,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEMO_ABSENCE_TIMEOUT_SECONDS,
    MANAGER_ID,
    MESSAGE_ACTUATOR_COMMAND,
    MESSAGE_ACK,
    MESSAGE_ERROR,
    MESSAGE_HELLO,
    MESSAGE_PRESENCE_UPDATE,
    MESSAGE_PROJECTOR_SWITCH,
    SOURCE_TYPE_MANAGER,
)
from smartroom.protocol.message import build_message  # noqa: E402
from smartroom.protocol.socket_utils import (  # noqa: E402
    ConnectionClosed,
    ProtocolSocketError,
    SocketMessageReader,
    send_message,
)


@dataclass
class ConnectedComponent:
    """Componente registrado apos uma mensagem HELLO valida."""

    source_id: str
    source_type: str
    component_role: str
    sock: socket.socket
    address: tuple[str, int]


class SmartRoomManager:
    """Servidor TCP principal dos componentes da sala inteligente."""

    def __init__(
        self,
        host: str,
        port: int,
        manual_mode: bool = False,
        demo_mode: bool = False,
    ):
        self.host = host
        self.port = port
        self.manual_mode = manual_mode
        self.demo_mode = demo_mode
        self.absence_timeout_seconds = (
            DEMO_ABSENCE_TIMEOUT_SECONDS if demo_mode else DEFAULT_ABSENCE_TIMEOUT_SECONDS
        )
        self.components: dict[str, ConnectedComponent] = {}
        self.components_lock = threading.Lock()
        self.presence_detected = False
        self.absence_started_at: float | None = None
        self.absence_timer: threading.Timer | None = None
        self.absence_lock = threading.Lock()
        self.stop_event = threading.Event()

    def start(self) -> None:
        """Aceita conexoes TCP ate haver interrupcao."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            server_socket.settimeout(1.0)

            self.log(f"Gerenciador escutando em {self.host}:{self.port}")
            if self.demo_mode:
                self.log(
                    "Modo demo ativo: ausencia prolongada usa "
                    f"{self.absence_timeout_seconds} segundos"
                )

            try:
                if self.manual_mode:
                    self.start_manual_command_thread()

                while not self.stop_event.is_set():
                    try:
                        client_socket, address = server_socket.accept()
                    except socket.timeout:
                        continue

                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True,
                    )
                    thread.start()
            except KeyboardInterrupt:
                self.log("Encerrando Gerenciador por interrupcao do usuario")
            finally:
                self.stop_event.set()
                self.cancel_absence_timer()
                self.close_all_components()

    def start_manual_command_thread(self) -> None:
        """Inicia uma thread para comandos manuais de atuadores."""

        thread = threading.Thread(target=self.manual_command_loop, daemon=True)
        thread.start()

    def manual_command_loop(self) -> None:
        """Permite enviar ACTUATOR_COMMAND pelo terminal do Gerenciador."""

        self.log("Modo manual ativo para comandos de atuadores")
        self.log("Digite: light on, light off, projector on, projector off, ac on, ac off")
        self.log("Digite: list para ver componentes conectados ou quit para encerrar")

        command_map = {
            "light": ACT_LIGHT_ID,
            "projector": ACT_PROJECTOR_ID,
            "ac": ACT_AC_ID,
        }

        while not self.stop_event.is_set():
            try:
                user_input = input("manager> ").strip().lower()
            except EOFError:
                self.stop_event.set()
                return

            if not user_input:
                continue

            if user_input in {"quit", "exit", "sair"}:
                self.stop_event.set()
                return

            if user_input == "list":
                self.list_registered_components()
                continue

            parts = user_input.split()
            if len(parts) != 2 or parts[0] not in command_map or parts[1] not in {"on", "off"}:
                self.log("Comando invalido. Use, por exemplo: light on")
                continue

            actuator_id = command_map[parts[0]]
            command = parts[1].upper()
            self.send_actuator_command(
                actuator_id=actuator_id,
                command=command,
                reason="manual_command",
            )

    def list_registered_components(self) -> None:
        """Imprime os componentes registrados no momento."""

        with self.components_lock:
            components = list(self.components.values())

        if not components:
            self.log("Nenhum componente conectado")
            return

        for component in components:
            self.log(
                "Conectado: "
                f"{component.source_id} ({component.source_type}/{component.component_role})"
            )

    def send_actuator_command(self, actuator_id: str, command: str, reason: str) -> bool:
        """Envia ACTUATOR_COMMAND para um atuador registrado."""

        with self.components_lock:
            component = self.components.get(actuator_id)

        if component is None:
            self.log(f"Atuador {actuator_id} nao esta conectado")
            return False

        message = build_message(
            message_type=MESSAGE_ACTUATOR_COMMAND,
            source_id=MANAGER_ID,
            source_type=SOURCE_TYPE_MANAGER,
            target_id=actuator_id,
            payload={
                "actuator_id": actuator_id,
                "command": command,
                "reason": reason,
            },
        )
        try:
            self.send_and_log(component.sock, message)
        except (OSError, ProtocolSocketError) as exc:
            self.log(f"Falha ao enviar comando para {actuator_id}: {exc}")
            self.unregister_component(actuator_id)
            self.close_socket(component.sock)
            return False

        return True

    def handle_client(self, client_socket: socket.socket, address: tuple[str, int]) -> None:
        """Trata uma conexao TCP."""

        component_id: str | None = None
        reader = SocketMessageReader(client_socket)
        self.log(f"Conexao recebida de {address[0]}:{address[1]}")

        try:
            hello_message = reader.receive()
            self.log_message("RECEBIDA", hello_message)

            component = self.register_component(hello_message, client_socket, address)
            component_id = component.source_id

            ack_message = build_message(
                message_type=MESSAGE_ACK,
                source_id=MANAGER_ID,
                source_type=SOURCE_TYPE_MANAGER,
                target_id=component.source_id,
                payload={"status": "registered"},
            )
            self.send_and_log(client_socket, ack_message)

            while not self.stop_event.is_set():
                message = reader.receive()
                self.log_message("RECEBIDA", message)
                self.process_protocol_message(message, client_socket)

        except ConnectionClosed:
            self.log_disconnect(component_id, address)
        except (ProtocolSocketError, ValueError) as exc:
            self.log(f"Mensagem invalida de {address[0]}:{address[1]}: {exc}")
            self.send_error(
                client_socket,
                target_id=component_id or "UNKNOWN",
                error_code="INVALID_MESSAGE",
                details=str(exc),
            )
        except OSError as exc:
            self.log(f"Erro de socket com {address[0]}:{address[1]}: {exc}")
        finally:
            self.unregister_component(component_id)
            self.close_socket(client_socket)

    def process_protocol_message(self, message: dict[str, Any], client_socket: socket.socket) -> None:
        """Processa mensagens recebidas depois do registro HELLO/ACK."""

        message_type = message["message_type"]

        if message_type == MESSAGE_ACK:
            self.log(f"ACK recebido de {message['source_id']}: {message['payload']}")
            return

        if message_type == MESSAGE_PRESENCE_UPDATE:
            self.handle_presence_update(message, client_socket)
            return

        if message_type == MESSAGE_PROJECTOR_SWITCH:
            self.handle_projector_switch(message, client_socket)
            return

        self.send_error(
            client_socket,
            target_id=message["source_id"],
            error_code="MESSAGE_NOT_IMPLEMENTED",
            details=f"Mensagem {message_type} ainda nao implementada no Gerenciador.",
        )

    def handle_presence_update(self, message: dict[str, Any], client_socket: socket.socket) -> None:
        """Aplica a regra inicial do sensor de presenca."""

        payload = message["payload"]
        presence_detected = payload.get("presence_detected")
        if not isinstance(presence_detected, bool):
            self.send_error(
                client_socket,
                target_id=message["source_id"],
                error_code="INVALID_PAYLOAD",
                details="payload.presence_detected deve ser booleano",
            )
            return

        self.presence_detected = presence_detected

        if presence_detected:
            self.log("Presenca detectada: ligando iluminacao e ar-condicionado")
            self.cancel_absence_timer()
            self.send_actuator_command(ACT_LIGHT_ID, "ON", "presence_detected")
            self.send_actuator_command(ACT_AC_ID, "ON", "presence_detected")
        else:
            self.start_absence_timer()

        ack_message = build_message(
            message_type=MESSAGE_ACK,
            source_id=MANAGER_ID,
            source_type=SOURCE_TYPE_MANAGER,
            target_id=message["source_id"],
            payload={
                "status": "presence_update_received",
                "presence_detected": presence_detected,
            },
        )
        self.send_and_log(client_socket, ack_message)

    def handle_projector_switch(self, message: dict[str, Any], client_socket: socket.socket) -> None:
        """Aplica a regra da chave ON/OFF do projetor."""

        payload = message["payload"]
        projector_switch_on = payload.get("projector_switch_on")
        if not isinstance(projector_switch_on, bool):
            self.send_error(
                client_socket,
                target_id=message["source_id"],
                error_code="INVALID_PAYLOAD",
                details="payload.projector_switch_on deve ser booleano",
            )
            return

        if projector_switch_on:
            self.log("Chave do projetor ligada: apagando luzes e ligando projetor")
            self.send_actuator_command(ACT_LIGHT_ID, "OFF", "projector_switch_on")
            self.send_actuator_command(ACT_PROJECTOR_ID, "ON", "projector_switch_on")
        else:
            self.log("Chave do projetor desligada: acendendo luzes e desligando projetor")
            self.send_actuator_command(ACT_LIGHT_ID, "ON", "projector_switch_off")
            self.send_actuator_command(ACT_PROJECTOR_ID, "OFF", "projector_switch_off")

        ack_message = build_message(
            message_type=MESSAGE_ACK,
            source_id=MANAGER_ID,
            source_type=SOURCE_TYPE_MANAGER,
            target_id=message["source_id"],
            payload={
                "status": "projector_switch_received",
                "projector_switch_on": projector_switch_on,
            },
        )
        self.send_and_log(client_socket, ack_message)

    def start_absence_timer(self) -> None:
        """Inicia ou reinicia o temporizador de ausencia prolongada."""

        with self.absence_lock:
            self.absence_started_at = time.monotonic()
            if self.absence_timer is not None:
                self.absence_timer.cancel()

            self.absence_timer = threading.Timer(
                self.absence_timeout_seconds,
                self.handle_absence_timeout,
            )
            self.absence_timer.daemon = True
            self.absence_timer.start()

        self.log(
            "Sala vazia: temporizador de ausencia iniciado "
            f"({self.absence_timeout_seconds} segundos)"
        )

    def cancel_absence_timer(self) -> None:
        """Cancela o temporizador de ausencia quando ha presenca novamente."""

        with self.absence_lock:
            if self.absence_timer is not None:
                self.absence_timer.cancel()
            self.absence_timer = None
            self.absence_started_at = None

    def handle_absence_timeout(self) -> None:
        """Desliga equipamentos apos ausencia prolongada."""

        with self.absence_lock:
            if self.presence_detected or self.absence_started_at is None:
                return

            elapsed = time.monotonic() - self.absence_started_at
            if elapsed < self.absence_timeout_seconds:
                return

            self.absence_timer = None

        self.log("Ausencia prolongada confirmada: desligando equipamentos")
        self.send_actuator_command(ACT_LIGHT_ID, "OFF", "absence_timeout")
        self.send_actuator_command(ACT_PROJECTOR_ID, "OFF", "absence_timeout")
        self.send_actuator_command(ACT_AC_ID, "OFF", "absence_timeout")

    def register_component(
        self,
        message: dict[str, Any],
        client_socket: socket.socket,
        address: tuple[str, int],
    ) -> ConnectedComponent:
        """Registra um componente apos validar a primeira mensagem HELLO."""

        if message["message_type"] != MESSAGE_HELLO:
            raise ValueError("primeira mensagem deve ser HELLO")

        component_role = message["payload"].get("component_role")
        if not isinstance(component_role, str) or not component_role.strip():
            raise ValueError("payload.component_role deve ser uma string nao vazia")

        source_id = message["source_id"]
        source_type = message["source_type"]

        with self.components_lock:
            if source_id in self.components:
                raise ValueError(f"componente ja conectado: {source_id}")

            component = ConnectedComponent(
                source_id=source_id,
                source_type=source_type,
                component_role=component_role,
                sock=client_socket,
                address=address,
            )
            self.components[source_id] = component

        self.log(
            "Componente registrado: "
            f"{source_id} ({source_type}/{component_role}) em {address[0]}:{address[1]}"
        )
        return component

    def unregister_component(self, component_id: str | None) -> None:
        """Remove um componente do registro ativo."""

        if not component_id:
            return

        with self.components_lock:
            removed = self.components.pop(component_id, None)

        if removed:
            self.log(f"Componente desconectado: {component_id}")

    def close_all_components(self) -> None:
        """Fecha todos os sockets registrados no momento."""

        with self.components_lock:
            components = list(self.components.values())
            self.components.clear()

        for component in components:
            self.close_socket(component.sock)

    def send_error(
        self,
        sock: socket.socket,
        target_id: str,
        error_code: str,
        details: str,
    ) -> None:
        """Envia uma mensagem ERROR do protocolo quando possivel."""

        error_message = build_message(
            message_type=MESSAGE_ERROR,
            source_id=MANAGER_ID,
            source_type=SOURCE_TYPE_MANAGER,
            target_id=target_id,
            payload={"error_code": error_code, "details": details},
        )
        try:
            self.send_and_log(sock, error_message)
        except (OSError, ProtocolSocketError) as exc:
            self.log(f"Nao foi possivel enviar ERROR para {target_id}: {exc}")

    def send_and_log(self, sock: socket.socket, message: dict[str, Any]) -> None:
        """Envia uma mensagem e imprime o payload completo do protocolo."""

        send_message(sock, message)
        self.log_message("ENVIADA", message)

    def log_message(self, direction: str, message: dict[str, Any]) -> None:
        """Imprime mensagens do protocolo em formato JSON legivel."""

        encoded = json.dumps(message, ensure_ascii=False)
        self.log(f"{direction}: {encoded}")

    def log_disconnect(self, component_id: str | None, address: tuple[str, int]) -> None:
        """Registra no log uma desconexao limpa do par."""

        if component_id:
            self.log(f"Conexao encerrada por {component_id}")
        else:
            self.log(f"Conexao encerrada por {address[0]}:{address[1]}")

    @staticmethod
    def close_socket(sock: socket.socket) -> None:
        try:
            sock.close()
        except OSError:
            pass

    @staticmethod
    def log(message: str) -> None:
        print(f"[MANAGER] {message}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gerenciador SMARTROOM/1.0")
    parser.add_argument("--host", default=DEFAULT_HOST, help="host TCP do Gerenciador")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="porta TCP do Gerenciador")
    parser.add_argument(
        "--manual",
        action="store_true",
        help="habilita menu manual para enviar comandos aos atuadores",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="usa 15 segundos para ausencia prolongada em vez de 15 minutos",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manager = SmartRoomManager(
        host=args.host,
        port=args.port,
        manual_mode=args.manual,
        demo_mode=args.demo,
    )
    manager.start()


if __name__ == "__main__":
    main()
