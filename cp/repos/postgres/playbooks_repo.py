"""Playbooks repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt
from ...models import Playbook, PlaybookOverview


def get_playbook(name: str, version: str) -> Playbook:
    return execute_stmt(
        """
        SELECT *
        FROM playbooks
        WHERE (name, version) = (%s, %s)
        """,
        (name, version),
        Playbook,
        return_list=False,
    )


def get_default_playbook(name: str) -> Playbook:
    return execute_stmt(
        """
        SELECT *
        FROM playbooks
        WHERE name = %s
        ORDER BY default_version DESC
        LIMIT 1
        """,
        (name,),
        Playbook,
        return_list=False,
    )


def list_playbook_versions(name: str) -> list[PlaybookOverview]:
    return execute_stmt(
        """
        SELECT name, version, default_version, created_at, created_by, updated_by
        FROM playbooks
        WHERE name = %s
        ORDER BY version DESC;
        """,
        (name,),
        PlaybookOverview,
        return_list=True,
    )


def add_playbook(name: str, playbook: bytes, created_by: str) -> PlaybookOverview:
    return execute_stmt(
        """
        INSERT INTO playbooks (name, playbook, created_by)
        VALUES (%s, %s, %s)
        RETURNING *
        """,
        (name, playbook, created_by),
        PlaybookOverview,
        return_list=False,
    )


def set_default_playbook(name: str, version: str, updated_by: str) -> None:
    execute_stmt(
        """
        UPDATE playbooks
        SET
            default_version = now(),
            updated_by = %s
        WHERE (name, version) = (%s, %s)
        """,
        (updated_by, name, version),
    )


def remove_playbook(name: str, version: str) -> None:
    execute_stmt(
        """
        DELETE
        FROM playbooks
        WHERE (name, version) = (%s, %s)
        """,
        (name, version),
    )
