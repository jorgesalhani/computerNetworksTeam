"""Funcoes compartilhadas do protocolo SMARTROOM/1.0."""

from .constants import PROTOCOL_ID
from .message import MessageValidationError, build_message, current_timestamp, validate_message
from .socket_utils import ConnectionClosed, ProtocolSocketError, SocketMessageReader, receive_message, send_message

__all__ = [
    "PROTOCOL_ID",
    "MessageValidationError",
    "build_message",
    "current_timestamp",
    "validate_message",
    "ConnectionClosed",
    "ProtocolSocketError",
    "SocketMessageReader",
    "receive_message",
    "send_message",
]
