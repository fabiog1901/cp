"""Alert API routes.

This router exposes Alertmanager-backed alert data for the webapp and API
clients. Alert retrieval and filtering live in AlertsService.
"""

from fastapi import APIRouter, Depends, Query
from cpkit.errors import raise_http_from_service_error

from ..cpkit_integration import require_readonly
from ..models import AlertmanagerPayload, LiveAlert
from ..services.alerts import AlertsService
from cpkit.errors import ServiceError

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
)


@router.get("/", response_model=list[LiveAlert])
async def list_alerts(
    limit: int | None = Query(default=None, ge=1, le=200),
    claims: dict = Depends(require_readonly),
    service: AlertsService = Depends(AlertsService),
) -> list[LiveAlert]:
    del claims
    try:
        return service.list_live_alerts(limit=limit)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/webhook")
async def receive_alert(
    payload: AlertmanagerPayload,
    service: AlertsService = Depends(AlertsService),
) -> dict[str, str]:
    try:
        service.ingest_payload(payload)
    except ServiceError as err:
        raise_http_from_service_error(err)

    return {"status": "ok"}
