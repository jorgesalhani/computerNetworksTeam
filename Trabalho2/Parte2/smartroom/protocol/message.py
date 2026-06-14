"""Message construction and validation for SMARTROOM/1.0."""

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
    """Raised when a protocol message is malformed."""


def current_timestamp() -> str:
    """Return a readable ISO-8601 timestamp without microseconds."""

    return datetime.now().replace(microsecond=0).isoformat()


def build_message(
    message_type: str,
    source_id: str,
    source_type: str,
    target_id: str,
    payload: dict[str, Any] | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build and validate a protocol message."""

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
    """Validate the common SMARTROOM/1.0 header and payload shape."""

    if not isinstance(message, dict):
        raise MessageValidationError("message must be a JSON object")

    missing_fields = [field for field in REQUIRED_FIELDS if field not in message]
    if missing_fields:
        raise MessageValidationError(f"missing required fields: {', '.join(missing_fields)}")

    if message["protocol_id"] != PROTOCOL_ID:
        raise MessageValidationError(f"invalid protocol_id: {message['protocol_id']!r}")

    if message["message_type"] not in MESSAGE_TYPES:
        raise MessageValidationError(f"invalid message_type: {message['message_type']!r}")

    if message["source_type"] not in SOURCE_TYPES:
        raise MessageValidationError(f"invalid source_type: {message['source_type']!r}")

    for field in ("source_id", "target_id", "timestamp"):
        if not isinstance(message[field], str) or not message[field].strip():
            raise MessageValidationError(f"{field} must be a non-empty string")

    if not isinstance(message["payload"], dict):
        raise MessageValidationError("payload must be a JSON object")

    return True
