"""Funcoes de socket para mensagens JSON delimitadas por quebra de linha."""

from __future__ import annotations

import json
import socket
from typing import Any

from .constants import MAX_MESSAGE_BYTES, SOCKET_BUFFER_SIZE
from .message import MessageValidationError, validate_message


class ProtocolSocketError(RuntimeError):
    """Erro gerado quando o payload do socket nao pode ser lido como protocolo."""


class ConnectionClosed(ProtocolSocketError):
    """Erro gerado quando o par fecha a conexao TCP."""


def send_message(sock: socket.socket, message: dict[str, Any]) -> None:
    """Envia uma mensagem JSON validada e terminada por quebra de linha."""

    try:
        validate_message(message)
    except MessageValidationError as exc:
        raise ProtocolSocketError(str(exc)) from exc

    encoded_message = json.dumps(message, ensure_ascii=False).encode("utf-8") + b"\n"
    sock.sendall(encoded_message)


def receive_message(sock: socket.socket, buffer: bytearray | None = None) -> dict[str, Any]:
    """Recebe uma mensagem JSON terminada por quebra de linha.

    Para leituras repetidas no mesmo socket, passe o mesmo buffer bytearray ou
    use SocketMessageReader para preservar bytes apos a quebra de linha.
    """

    read_buffer = buffer if buffer is not None else bytearray()

    while b"\n" not in read_buffer:
        chunk = sock.recv(SOCKET_BUFFER_SIZE)
        if not chunk:
            raise ConnectionClosed("conexao fechada pelo par")
        read_buffer.extend(chunk)
        if len(read_buffer) > MAX_MESSAGE_BYTES:
            raise ProtocolSocketError("mensagem excede o tamanho maximo")

    line, _, remaining = read_buffer.partition(b"\n")
    read_buffer[:] = remaining

    if not line.strip():
        return receive_message(sock, read_buffer)

    try:
        message = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolSocketError(f"mensagem JSON invalida: {exc}") from exc

    try:
        validate_message(message)
    except MessageValidationError as exc:
        raise ProtocolSocketError(str(exc)) from exc

    return message


class SocketMessageReader:
    """Leitor com estado que preserva dados parciais entre leituras TCP."""

    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.buffer = bytearray()

    def receive(self) -> dict[str, Any]:
        return receive_message(self.sock, self.buffer)
