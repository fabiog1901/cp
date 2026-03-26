from fastapi import APIRouter, Depends

from ...auth import get_audit_actor
from ...infra import get_playbooks_service
from ...models import (
    PlaybookName,
    PlaybookSaveRequest,
    PlaybookResponse,
    PlaybookSetDefaultRequest,
    PlaybookVersionDeleteRequest,
    PlaybookVersionResponse,
)
from ...services.errors import ServiceError
from ...services.playbooks import PlaybooksService
from .common import raise_http_from_service_error

router = APIRouter(prefix="/playbooks", tags=["admin"])


@router.get("/{name}", response_model=PlaybookResponse)
async def get_playbook(
    name: PlaybookName,
    service: PlaybooksService = Depends(get_playbooks_service),
) -> PlaybookResponse:
    try:
        return service.load_playbook_selection(name)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.get("/{name}/{version}", response_model=PlaybookVersionResponse)
async def get_playbook_version(
    name: PlaybookName,
    version: str,
    service: PlaybooksService = Depends(get_playbooks_service),
) -> PlaybookVersionResponse:
    try:
        return PlaybookVersionResponse(**service.load_playbook_version(name, version))
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/{name}", response_model=PlaybookVersionResponse)
async def save_playbook(
    name: PlaybookName,
    request: PlaybookSaveRequest,
    actor_id: str = Depends(get_audit_actor),
    service: PlaybooksService = Depends(get_playbooks_service),
) -> PlaybookVersionResponse:
    try:
        return service.save_playbook_content(name, request.content, actor_id)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.put("/{name}/default")
async def set_default_playbook(
    name: PlaybookName,
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
    name: PlaybookName,
    version: str,
    request: PlaybookVersionDeleteRequest,
    actor_id: str = Depends(get_audit_actor),
    service: PlaybooksService = Depends(get_playbooks_service),
) -> PlaybookVersionResponse:
    try:
        return service.delete_playbook_version(
            name,
            version,
            request.default_version,
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
