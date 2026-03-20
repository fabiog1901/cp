"""Event repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_scalar
from ...models import EventLog


def list_events(
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
        )

    return []


def get_event_count() -> int:
    return fetch_scalar(
        """
        SELECT count(*) AS id
        FROM event_log AS OF SYSTEM TIME follower_read_timestamp()
        """,
        (),
    )


def insert_event_log(
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
    )
