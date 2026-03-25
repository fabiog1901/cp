from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..auth import get_access_scope, require_readonly
from ..infra import get_events_service
from ..models import EventCountResponse, LogMsg
from ..services.errors import (
    ServiceAuthorizationError,
    ServiceError,
    ServiceNotFoundError,
    ServiceUnavailableError,
    ServiceValidationError,
)
from ..services.events import EventsService

router = APIRouter(
    prefix="/events",
    tags=["events"],
)


def _raise_http_from_service_error(err: ServiceError) -> None:
    if isinstance(err, ServiceNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=err.user_message,
        )
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


@router.get("/")
async def list_events(
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    claims: dict = Depends(require_readonly),
    service: EventsService = Depends(get_events_service),
) -> list[LogMsg]:
    groups, is_admin = get_access_scope(claims)
    try:
        return service.list_visible_events(limit, offset, groups, is_admin)
    except ServiceError as err:
        _raise_http_from_service_error(err)


@router.get("/count", response_model=EventCountResponse)
async def get_event_count(
    service: EventsService = Depends(get_events_service),
) -> EventCountResponse:
    try:
        total = service.get_event_total()
    except ServiceError as err:
        _raise_http_from_service_error(err)

    return EventCountResponse(total=total)
