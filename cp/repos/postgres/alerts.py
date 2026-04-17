"""Alerts repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt, fetch_all
from ...models import LiveAlert
from ..base import BaseRepo


class AlertsRepo(BaseRepo):
    def list_live_alerts(self) -> list[LiveAlert]:
        return fetch_all(
            """
            SELECT
                fingerprint,
                alert_type,
                cluster,
                nodes,
                summary,
                description,
                starts_at,
                ends_at
            FROM live_alerts
            ORDER BY starts_at DESC, updated_at DESC
            """,
            (),
            LiveAlert,
            operation="alerts.list_live_alerts",
        )

    def upsert_live_alert(self, alert: LiveAlert) -> None:
        execute_stmt(
            """
            INSERT INTO live_alerts (
                fingerprint,
                alert_type,
                cluster,
                nodes,
                summary,
                description,
                starts_at,
                ends_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (fingerprint) DO UPDATE
            SET
                alert_type = excluded.alert_type,
                cluster = excluded.cluster,
                nodes = excluded.nodes,
                summary = excluded.summary,
                description = excluded.description,
                starts_at = excluded.starts_at,
                ends_at = excluded.ends_at,
                updated_at = now()
            """,
            (
                alert.fingerprint,
                alert.alert_type,
                alert.cluster,
                alert.nodes,
                alert.summary,
                alert.description,
                alert.starts_at,
                alert.ends_at,
            ),
            operation="alerts.upsert_live_alert",
        )
