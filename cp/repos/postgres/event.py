"""Event repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_scalar
from ...models import LogMsg
from ..base import BaseRepo


class EventRepo(BaseRepo):
    def list_events(
        self,
        limit: int,
        offset: int,
        groups: list[str] | None = None,
        is_admin: bool = False,
    ) -> list[LogMsg]:
        if is_admin:
            return fetch_all(
                """
                SELECT *
                FROM event_log
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
            """
            SELECT count(*) AS id
            FROM event_log AS OF SYSTEM TIME follower_read_timestamp()
            """,
            (),
            operation="events.get_event_count",
        )

    def log_event(self, log_msg: LogMsg):
        execute_stmt(
            """
            INSERT INTO event_log 
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
