"""Cliente TCP base para componentes SMARTROOM/1.0."""

from __future__ import annotations

import argparse
import json
import socket
from typing import Any, Callable

from smartroom.protocol.constants import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    MANAGER_ID,
    MESSAGE_ACK,
    MESSAGE_ERROR,
    MESSAGE_HELLO,
)
from smartroom.protocol.message import build_message
from smartroom.protocol.socket_utils import (
    ConnectionClosed,
    ProtocolSocketError,
    SocketMessageReader,
    send_message,
)


class ClienteComponenteTCP:
    """Cliente TCP reutilizavel para sensores, atuadores e cliente/professor."""

    def __init__(
        self,
        host: str,
        port: int,
        source_id: str,
        source_type: str,
        component_role: str,
        log_prefix: str,
    ):
        self.host = host
        self.port = port
        self.source_id = source_id
        self.source_type = source_type
        self.component_role = component_role
        self.log_prefix = log_prefix
        self.sock: socket.socket | None = None
        self.reader: SocketMessageReader | None = None

    def conectar(self) -> None:
        """Conecta ao Gerenciador e realiza o registro HELLO/ACK."""

        self.sock = socket.create_connection((self.host, self.port))
        self.reader = SocketMessageReader(self.sock)
        self.log(f"Conectado ao Gerenciador em {self.host}:{self.port}")

        hello_message = self.criar_mensagem(
            message_type=MESSAGE_HELLO,
            payload={"component_role": self.component_role},
        )
        self.enviar(hello_message)

        response = self.receber()
        if response["message_type"] != MESSAGE_ACK:
            raise RuntimeError(f"registro recusado: esperado ACK, recebido {response['message_type']}")

        status = response["payload"].get("status")
        if status != "registered":
            raise RuntimeError(f"registro recusado: status {status!r}")

        self.log("Registro confirmado pelo Gerenciador")

    def escutar(self, on_message: Callable[[dict[str, Any]], None]) -> None:
        """Recebe mensagens ate a conexao ser encerrada."""

        if self.reader is None:
            raise RuntimeError("cliente nao conectado")

        while True:
            try:
                message = self.receber()
            except ConnectionClosed:
                self.log("Conexao encerrada pelo Gerenciador")
                return

            on_message(message)

    def criar_mensagem(
        self,
        message_type: str,
        payload: dict[str, Any] | None = None,
        target_id: str = MANAGER_ID,
    ) -> dict[str, Any]:
        """Cria uma mensagem usando os dados de origem do componente."""

        return build_message(
            message_type=message_type,
            source_id=self.source_id,
            source_type=self.source_type,
            target_id=target_id,
            payload=payload or {},
        )

    def enviar_ack(self, status: str, payload: dict[str, Any] | None = None) -> None:
        """Envia ACK ao Gerenciador."""

        ack_payload = {"status": status}
        if payload:
            ack_payload.update(payload)

        self.enviar(self.criar_mensagem(message_type=MESSAGE_ACK, payload=ack_payload))

    def enviar_erro(self, error_code: str, details: str) -> None:
        """Envia ERROR ao Gerenciador."""

        self.enviar(
            self.criar_mensagem(
                message_type=MESSAGE_ERROR,
                payload={"error_code": error_code, "details": details},
            )
        )

    def enviar(self, message: dict[str, Any]) -> None:
        """Envia uma mensagem pelo socket conectado."""

        if self.sock is None:
            raise RuntimeError("cliente nao conectado")

        send_message(self.sock, message)
        self.log_message("ENVIADA", message)

    def receber(self) -> dict[str, Any]:
        """Recebe uma mensagem pelo socket conectado."""

        if self.reader is None:
            raise RuntimeError("cliente nao conectado")

        message = self.reader.receive()
        self.log_message("RECEBIDA", message)
        return message

    def fechar(self) -> None:
        """Fecha o socket do componente."""

        if self.sock is not None:
            self.sock.close()
            self.sock = None
            self.reader = None

    def log_message(self, direction: str, message: dict[str, Any]) -> None:
        encoded = json.dumps(message, ensure_ascii=False)
        self.log(f"{direction}: {encoded}")

    def log(self, message: str) -> None:
        print(f"[{self.log_prefix}] {message}", flush=True)


def criar_parser_conexao(description: str) -> argparse.ArgumentParser:
    """Cria parser padrao com host e porta do Gerenciador."""

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--host", default=DEFAULT_HOST, help="host TCP do Gerenciador")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="porta TCP do Gerenciador")
    return parser
