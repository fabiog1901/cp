"""Event repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_scalar
from ...models import EventLog, LogMsg
from ..base import BaseRepo


class EventRepo(BaseRepo):
    def list_events(
        self,
        limit: int,
        offset: int,
        groups: list[str] | None = None,
        is_admin: bool = False,
    ) -> list[EventLog]:
        if is_admin:
            return fetch_all(
                """
                SELECT *
                FROM event_log
                ORDER BY created_at DESC
                LIMIT %s
                OFFSET %s
                """,
                (limit, offset),
                EventLog,
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

    def insert_event_log(
        self,
        created_by: str,
        event_type: str,
        event_details=None,
    ) -> None:
        execute_stmt(
            """
            INSERT INTO event_log (
                created_by, event_type, event_details)
            VALUES
                (%s, %s, %s)
            """,
            (
                created_by,
                event_type,
                event_details,
            ),
            operation="events.insert_event_log",
        )

    def log_event(self, event: LogMsg):
        execute_stmt(
            """
                    INSERT INTO event_log (ts, user_id, action, details, request_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
            (
                event.ts,
                event.user_id,
                event.action,
                event.details,
                event.request_id,
            ),
        )
