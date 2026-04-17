"""Alerts repository backed by CockroachDB/Postgres."""

from ...infra.db import execute_stmt
from ...models import LiveAlert
from ..base import BaseRepo


class AlertsRepo(BaseRepo):
    def upsert_live_alert(self, alert: LiveAlert) -> None:
        execute_stmt(
            """
            INSERT INTO live_alerts (
                fingerprint,
                receiver,
                payload_status,
                alert_name,
                severity,
                status,
                labels,
                annotations,
                starts_at,
                ends_at,
                group_labels,
                common_labels,
                common_annotations,
                external_url
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (fingerprint) DO UPDATE
            SET
                receiver = excluded.receiver,
                payload_status = excluded.payload_status,
                alert_name = excluded.alert_name,
                severity = excluded.severity,
                status = excluded.status,
                labels = excluded.labels,
                annotations = excluded.annotations,
                starts_at = excluded.starts_at,
                ends_at = excluded.ends_at,
                group_labels = excluded.group_labels,
                common_labels = excluded.common_labels,
                common_annotations = excluded.common_annotations,
                external_url = excluded.external_url,
                updated_at = now()
            """,
            (
                alert.fingerprint,
                alert.receiver,
                alert.payload_status,
                alert.alert_name,
                alert.severity,
                alert.status,
                alert.labels,
                alert.annotations,
                alert.starts_at,
                alert.ends_at,
                alert.group_labels,
                alert.common_labels,
                alert.common_annotations,
                alert.external_url,
            ),
            operation="alerts.upsert_live_alert",
        )
