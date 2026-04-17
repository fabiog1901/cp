"""Business logic for the alerts vertical."""

from ..infra.errors import RepositoryError
from ..models import AlertmanagerPayload, LiveAlert
from ..repos.base import BaseRepo
from .errors import from_repository_error


class AlertsService:
    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo

    def ingest_payload(self, payload: AlertmanagerPayload) -> None:
        try:
            for alert in payload.alerts:
                self.repo.upsert_live_alert(
                    LiveAlert(
                        fingerprint=alert.fingerprint,
                        receiver=payload.receiver,
                        payload_status=payload.status,
                        alert_name=alert.labels.get("alertname"),
                        severity=alert.labels.get("severity"),
                        status=alert.status,
                        labels=alert.labels,
                        annotations=alert.annotations,
                        starts_at=alert.startsAt,
                        ends_at=alert.endsAt,
                        group_labels=payload.groupLabels,
                        common_labels=payload.commonLabels,
                        common_annotations=payload.commonAnnotations,
                        external_url=payload.externalURL,
                    )
                )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="Alert ingestion is temporarily unavailable.",
                validation_message="The alert payload could not be stored.",
                fallback_message="Unable to store alert payload.",
            ) from err
