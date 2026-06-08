"""Repository helpers for the framework message queue."""

from typing import Any

from cpkit.db import execute_stmt

QUEUE_TABLE = "cpkit.mq"


class QueueRepositoryMixin:
    """Repository mixin for enqueueing framework queue messages."""

    def enqueue_message(
        self,
        msg_type: Any,
        payload: Any | None,
        created_by: str,
        *,
        start_after_seconds: int = 0,
    ) -> None:
        """Enqueue a message to be processed by the framework worker."""
        execute_stmt(
            f"""
            INSERT INTO {QUEUE_TABLE}
                (msg_type, msg_data, created_by, start_after)
            VALUES
                (%s, %s, %s, now() + (%s * INTERVAL '1s'))
            """,
            (
                _message_type_value(msg_type),
                _payload_value(payload),
                created_by,
                start_after_seconds,
            ),
            operation="jobs.enqueue_message",
        )


def _message_type_value(msg_type: Any) -> str:
    return str(getattr(msg_type, "value", msg_type))


def _payload_value(payload: Any | None) -> dict[str, Any]:
    if payload is None:
        return {}
    if hasattr(payload, "model_dump"):
        return payload.model_dump()
    if isinstance(payload, dict):
        return payload
    raise TypeError("Queue message payload must be a mapping or Pydantic model.")
