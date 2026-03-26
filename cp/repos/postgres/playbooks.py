"""Playbooks repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all, fetch_one
from ...models import Playbook, PlaybookOverview
from ..base import BaseRepo


class PlaybooksRepo(BaseRepo):
    def get_playbook(self, name: str, version: str) -> Playbook:
        return fetch_one(
            """
            SELECT *
            FROM playbooks
            WHERE (name, version) = (%s, %s)
            """,
            (name, version),
            Playbook,
        )

    def get_default_playbook(self, name: str) -> Playbook:
        return fetch_one(
            """
            SELECT *
            FROM playbooks
            WHERE name = %s
            ORDER BY default_version DESC NULLS LAST, version DESC
            LIMIT 1
            """,
            (name,),
            Playbook,
        )

    def list_playbook_versions(self, name: str) -> list[PlaybookOverview]:
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

    def add_playbook(
        self,
        name: str,
        content: bytes,
        created_by: str,
    ) -> PlaybookOverview:
        return fetch_one(
            """
            INSERT INTO playbooks (name, content, created_by)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (name, content, created_by),
            PlaybookOverview,
        )

    def set_default_playbook(self, name: str, version: str, updated_by: str) -> None:
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

    def remove_playbook(self, name: str, version: str) -> None:
        execute_stmt(
            """
            DELETE
            FROM playbooks
            WHERE (name, version) = (%s, %s)
            """,
            (name, version),
        )


# def playbook_get_content(self, playbook: Playbook) -> str:

#     with self.pool.connection() as conn:

#         cur = conn.cursor()
#         rs = cur.execute(
#             """
#             SELECT content
#             FROM playbooks
#             WHERE id = %s
#             """,
#             (playbook,),
#         ).fetchone()

#     return gzip.decompress(rs[0]).decode()  # type: ignore

# def playbook_update_content(
#     self,
#     playbook: Playbook,
#     b64: str,
# ) -> None:

#     with self.pool.connection() as conn:

#         cur = conn.cursor()
#         cur.execute(
#             """
#             UPDATE playbooks
#             SET content = %s
#             WHERE id = %s
#             """,
#             (
#                 gzip.compress(b64.encode()),
#                 playbook,
#             ),
#         )
