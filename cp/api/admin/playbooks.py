from fastapi import APIRouter, Depends

from ...auth import get_audit_actor
from ...infra import get_playbooks_service
from ...models import (
    PlaybookSaveRequest,
    PlaybookSelectionResponse,
    PlaybookSetDefaultRequest,
    PlaybookVersionDeleteRequest,
    PlaybookVersionResponse,
)
from ...services.errors import ServiceError
from ...services.playbooks import PlaybooksService
from .common import raise_http_from_service_error

router = APIRouter(prefix="/playbooks", tags=["admin"])


@router.get("/{name}", response_model=PlaybookSelectionResponse)
async def get_playbook_selection(
    name: str,
    service: PlaybooksService = Depends(get_playbooks_service),
) -> PlaybookSelectionResponse:
    try:
        return PlaybookSelectionResponse(**service.load_playbook_selection(name))
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.get("/{name}/{version}", response_model=PlaybookVersionResponse)
async def get_playbook_version(
    name: str,
    version: str,
    service: PlaybooksService = Depends(get_playbooks_service),
) -> PlaybookVersionResponse:
    try:
        return PlaybookVersionResponse(**service.load_playbook_version(name, version))
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/{name}", response_model=PlaybookVersionResponse)
async def save_playbook(
    name: str,
    request: PlaybookSaveRequest,
    actor_id: str = Depends(get_audit_actor),
    service: PlaybooksService = Depends(get_playbooks_service),
) -> PlaybookVersionResponse:
    try:
        return PlaybookVersionResponse(
            **service.save_playbook_content(name, request.content, actor_id)
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.put("/{name}/default")
async def set_default_playbook(
    name: str,
    request: PlaybookSetDefaultRequest,
    actor_id: str = Depends(get_audit_actor),
    service: PlaybooksService = Depends(get_playbooks_service),
) -> None:
    try:
        service.set_default_playbook(name, request.version, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{name}/{version}", response_model=PlaybookVersionResponse)
async def delete_playbook_version(
    name: str,
    version: str,
    request: PlaybookVersionDeleteRequest,
    actor_id: str = Depends(get_audit_actor),
    service: PlaybooksService = Depends(get_playbooks_service),
) -> PlaybookVersionResponse:
    try:
        return PlaybookVersionResponse(
            **service.delete_playbook_version(
                name,
                version,
                request.default_version,
                actor_id,
            )
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
