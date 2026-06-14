"""Construcao e validacao de mensagens SMARTROOM/1.0."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .constants import MESSAGE_TYPES, PROTOCOL_ID, SOURCE_TYPES

REQUIRED_FIELDS = (
    "protocol_id",
    "message_type",
    "source_id",
    "source_type",
    "target_id",
    "timestamp",
    "payload",
)


class MessageValidationError(ValueError):
    """Erro gerado quando uma mensagem do protocolo esta malformada."""


def current_timestamp() -> str:
    """Retorna um timestamp ISO-8601 legivel, sem microssegundos."""

    return datetime.now().replace(microsecond=0).isoformat()


def build_message(
    message_type: str,
    source_id: str,
    source_type: str,
    target_id: str,
    payload: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Monta e valida uma mensagem do protocolo."""

    message = {
        "protocol_id": PROTOCOL_ID,
        "message_type": message_type,
        "source_id": source_id,
        "source_type": source_type,
        "target_id": target_id,
        "timestamp": timestamp or current_timestamp(),
        "payload": payload or {},
    }
    validate_message(message)
    return message


def validate_message(message: Any) -> bool:
    """Valida o header comum e a estrutura do payload SMARTROOM/1.0."""

    if not isinstance(message, dict):
        raise MessageValidationError("mensagem deve ser um objeto JSON")

    missing_fields = [field for field in REQUIRED_FIELDS if field not in message]
    if missing_fields:
        raise MessageValidationError(f"campos obrigatorios ausentes: {', '.join(missing_fields)}")

    if message["protocol_id"] != PROTOCOL_ID:
        raise MessageValidationError(f"protocol_id invalido: {message['protocol_id']!r}")

    if message["message_type"] not in MESSAGE_TYPES:
        raise MessageValidationError(f"message_type invalido: {message['message_type']!r}")

    if message["source_type"] not in SOURCE_TYPES:
        raise MessageValidationError(f"source_type invalido: {message['source_type']!r}")

    for field in ("source_id", "target_id", "timestamp"):
        if not isinstance(message[field], str) or not message[field].strip():
            raise MessageValidationError(f"{field} deve ser uma string nao vazia")

    if not isinstance(message["payload"], dict):
        raise MessageValidationError("payload deve ser um objeto JSON")

    return True
