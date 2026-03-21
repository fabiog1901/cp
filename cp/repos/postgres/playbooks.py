"""Playbooks repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_one
from ...models import Playbook, PlaybookOverview


class PlaybooksRepo:
    @staticmethod
    def get_playbook(name: str, version: str) -> Playbook:
        return fetch_one(
            """
            SELECT *
            FROM playbooks
            WHERE (name, version) = (%s, %s)
            """,
            (name, version),
            Playbook,
        )

    @staticmethod
    def get_default_playbook(name: str) -> Playbook:
        return fetch_one(
            """
            SELECT *
            FROM playbooks
            WHERE name = %s
            ORDER BY default_version DESC
            LIMIT 1
            """,
            (name,),
            Playbook,
        )

    @staticmethod
    def list_playbook_versions(name: str) -> list[PlaybookOverview]:
        return fetch_all(
            """
            SELECT name, version, default_version, created_at, created_by, updated_by
            FROM playbooks
            WHERE name = %s
            ORDER BY version DESC;
            """,
            (name,),
            PlaybookOverview,
        )

    @staticmethod
    def add_playbook(name: str, playbook: bytes, created_by: str) -> PlaybookOverview:
        return fetch_one(
            """
            INSERT INTO playbooks (name, playbook, created_by)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (name, playbook, created_by),
            PlaybookOverview,
        )

    @staticmethod
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

    @staticmethod
    def remove_playbook(name: str, version: str) -> None:
        execute_stmt(
            """
            DELETE
            FROM playbooks
            WHERE (name, version) = (%s, %s)
            """,
            (name, version),
        )
