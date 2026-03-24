from fastapi import APIRouter, Depends, Query

from ...infra import get_events_service
from ...models import EventCountResponse, EventLog
from ...services.errors import ServiceError
from ...services.events import EventsService
from .common import raise_http_from_service_error

router = APIRouter(prefix="/events", tags=["admin"])


@router.get("/")
async def list_events(
    limit: int = Query(default=20, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service: EventsService = Depends(get_events_service),
) -> list[EventLog]:
    try:
        return service.list_visible_events(limit, offset, [], True)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.get("/count", response_model=EventCountResponse)
async def get_event_count(
    service: EventsService = Depends(get_events_service),
) -> EventCountResponse:
    try:
        return EventCountResponse(total=service.get_event_total())
    except ServiceError as err:
        raise_http_from_service_error(err)
