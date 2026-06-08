"""Generic queue worker loop."""

import asyncio
import logging
import random
from collections.abc import Callable, Mapping
from typing import Any

from psycopg.rows import class_row

from .repository import QUEUE_TABLE
from .types import QueueMessage

logger = logging.getLogger(__name__)

QueueHandler = Callable[[int, Any, str], None]
ResolveHandler = Callable[[QueueMessage], QueueHandler | None]
ParseMessage = Callable[[QueueMessage], Any]
FailureHandler = Callable[[QueueMessage, Exception], None]


async def run_queue_worker(
    *,
    get_pool: Callable[[], Any],
    handlers: Mapping[Any, QueueHandler] | None = None,
    resolve_handler: ResolveHandler | None = None,
    parse_message: ParseMessage | None = None,
    handle_failure: FailureHandler | None = None,
    poll_seconds: float = 5,
    jitter_min: float = 0.7,
    jitter_max: float = 1.3,
) -> None:
    """Continuously claim due queue messages and dispatch them to handlers."""
    try:
        while True:
            await asyncio.sleep(poll_seconds * random.uniform(jitter_min, jitter_max))
            try:
                with get_pool().connection() as conn:
                    with conn.cursor(row_factory=class_row(QueueMessage)) as cur:
                        with conn.transaction():
                            message = _claim_due_message(cur)
                            if message is None:
                                continue

                            logger.info(
                                "Processing queue message %s of type %s",
                                message.msg_id,
                                message.msg_type,
                            )

                            try:
                                handler = _resolve_handler(
                                    message,
                                    handlers=handlers,
                                    resolve_handler=resolve_handler,
                                )
                                payload = (
                                    parse_message(message)
                                    if parse_message is not None
                                    else message.msg_data
                                )
                                handler(message.msg_id, payload, message.created_by)
                            except Exception as err:
                                logger.exception(
                                    "Queue message %s failed during dispatch",
                                    message.msg_id,
                                )
                                if handle_failure is not None:
                                    try:
                                        handle_failure(message, err)
                                    except Exception:
                                        logger.exception(
                                            "Queue message %s failure hook failed",
                                            message.msg_id,
                                        )
                            finally:
                                cur.execute(
                                    f"DELETE FROM {QUEUE_TABLE} WHERE msg_id = %s;",
                                    (message.msg_id,),
                                )
            except Exception:
                logger.exception("Unexpected failure while polling the message queue")

    except asyncio.CancelledError:
        logger.info("Queue worker was stopped")


def _claim_due_message(cur) -> QueueMessage | None:
    return cur.execute(
        f"""
        SELECT *
        FROM {QUEUE_TABLE}
        WHERE now() > start_after
        LIMIT 1
        FOR UPDATE SKIP LOCKED
        """
    ).fetchone()


def _resolve_handler(
    message: QueueMessage,
    *,
    handlers: Mapping[Any, QueueHandler] | None,
    resolve_handler: ResolveHandler | None,
) -> QueueHandler:
    if resolve_handler is not None:
        handler = resolve_handler(message)
    elif handlers is not None:
        handler = handlers.get(message.msg_type)
    else:
        handler = None

    if handler is None:
        raise ValueError(f"Unknown task type requested: {message.msg_type}")
    return handler
