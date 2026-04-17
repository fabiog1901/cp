from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import require_readonly
from ..infra import get_alerts_service
from ..models import AlertmanagerPayload, LiveAlert
from ..services.alerts import AlertsService
from ..services.errors import (
    ServiceAuthorizationError,
    ServiceError,
    ServiceUnavailableError,
    ServiceValidationError,
)

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
)


def _raise_http_from_service_error(err: ServiceError) -> None:
    if isinstance(err, ServiceValidationError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.user_message,
        )
    if isinstance(err, ServiceAuthorizationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=err.user_message,
        )
    if isinstance(err, ServiceUnavailableError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=err.user_message,
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=err.user_message,
    )


@router.get("/", response_model=list[LiveAlert])
async def list_alerts(
    claims: dict = Depends(require_readonly),
    service: AlertsService = Depends(get_alerts_service),
) -> list[LiveAlert]:
    del claims
    try:
        return service.list_live_alerts()
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.post("/webhook")
async def receive_alert(
    payload: AlertmanagerPayload,
    service: AlertsService = Depends(get_alerts_service),
) -> dict[str, str]:
    try:
        service.ingest_payload(payload)
    except ServiceError as err:
        _raise_http_from_service_error(err)

    return {"status": "ok"}
