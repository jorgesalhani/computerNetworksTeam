"""Socket helpers for newline-delimited JSON protocol messages."""

from __future__ import annotations

import json
import socket
from typing import Any

from .constants import MAX_MESSAGE_BYTES, SOCKET_BUFFER_SIZE
from .message import MessageValidationError, validate_message


class ProtocolSocketError(RuntimeError):
    """Raised when a socket payload cannot be parsed as a protocol message."""


class ConnectionClosed(ProtocolSocketError):
    """Raised when the peer closes the TCP connection."""


def send_message(sock: socket.socket, message: dict[str, Any]) -> None:
    """Send one validated JSON message terminated by a newline."""

    try:
        validate_message(message)
    except MessageValidationError as exc:
        raise ProtocolSocketError(str(exc)) from exc

    encoded_message = json.dumps(message, ensure_ascii=False).encode("utf-8") + b"\n"
    sock.sendall(encoded_message)


def receive_message(sock: socket.socket, buffer: bytearray | None = None) -> dict[str, Any]:
    """Receive one JSON message terminated by a newline.

    For repeated reads on the same socket, pass the same bytearray buffer or
    use SocketMessageReader so bytes after the newline are preserved.
    """

    read_buffer = buffer if buffer is not None else bytearray()

    while b"\n" not in read_buffer:
        chunk = sock.recv(SOCKET_BUFFER_SIZE)
        if not chunk:
            raise ConnectionClosed("connection closed by peer")
        read_buffer.extend(chunk)
        if len(read_buffer) > MAX_MESSAGE_BYTES:
            raise ProtocolSocketError("message exceeds maximum size")

    line, _, remaining = read_buffer.partition(b"\n")
    read_buffer[:] = remaining

    if not line.strip():
        return receive_message(sock, read_buffer)

    try:
        message = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolSocketError(f"invalid JSON message: {exc}") from exc

    try:
        validate_message(message)
    except MessageValidationError as exc:
        raise ProtocolSocketError(str(exc)) from exc

    return message


class SocketMessageReader:
    """Stateful reader that preserves partial data between TCP reads."""

    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.buffer = bytearray()

    def receive(self) -> dict[str, Any]:
        return receive_message(self.sock, self.buffer)
