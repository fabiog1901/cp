"""Event repository."""

from cpkit.audit import EVENT_LOG_TABLE
from cpkit.db import execute_stmt, fetch_all, fetch_scalar

from ..models import LogMsg


class EventRepo:
    def list_events(
        self,
        limit: int,
        offset: int,
        groups: list[str] | None = None,
        is_admin: bool = False,
    ) -> list[LogMsg]:
        if is_admin:
            return fetch_all(
                f"""
                SELECT ts, user_id, action, details, request_id::TEXT
                FROM {EVENT_LOG_TABLE}
                ORDER BY ts DESC
                LIMIT %s
                OFFSET %s
                """,
                (limit, offset),
                LogMsg,
                operation="events.list_events",
            )

        return []

    def get_event_count(self) -> int:
        return fetch_scalar(
            f"""
            SELECT count(*) AS id
            FROM {EVENT_LOG_TABLE} AS OF SYSTEM TIME follower_read_timestamp()
            """,
            (),
            operation="events.get_event_count",
        )

    def log_event(self, log_msg: LogMsg):
        execute_stmt(
            f"""
            INSERT INTO {EVENT_LOG_TABLE}
                (ts, user_id, action, details, request_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                log_msg.ts,
                log_msg.user_id,
                log_msg.action,
                log_msg.details,
                log_msg.request_id,
            ),
        )
