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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from smartroom.protocol.constants import (  # noqa: E402
    DEFAULT_HOST,
    DEFAULT_PORT,
    MANAGER_ID,
    MESSAGE_ACK,
    MESSAGE_ERROR,
    MESSAGE_HELLO,
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

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.components: dict[str, ConnectedComponent] = {}
        self.components_lock = threading.Lock()
        self.stop_event = threading.Event()

    def start(self) -> None:
        """Aceita conexoes TCP ate haver interrupcao."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            server_socket.settimeout(1.0)

            self.log(f"Gerenciador escutando em {self.host}:{self.port}")

            try:
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
                self.close_all_components()

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
                self.send_error(
                    client_socket,
                    target_id=message["source_id"],
                    error_code="MESSAGE_NOT_IMPLEMENTED",
                    details=(
                        "Gerenciador minimo registra componentes, mas as regras "
                        "funcionais serao implementadas nos proximos blocos."
                    ),
                )

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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manager = SmartRoomManager(host=args.host, port=args.port)
    manager.start()


if __name__ == "__main__":
    main()
