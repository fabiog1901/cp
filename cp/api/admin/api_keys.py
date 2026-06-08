from fastapi import APIRouter, Depends

from ...auth import get_audit_actor
from ...models import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeySummary,
    ErrorResponse,
)
from ...services.admin.api_keys import ApiKeysService
from ...services.errors import ServiceError
from .common import raise_http_from_service_error

router = APIRouter(prefix="/api_keys", tags=["admin"])


@router.get("/")
async def list_api_keys(
    access_key: str | None = None,
    service: ApiKeysService = Depends(ApiKeysService),
) -> list[ApiKeySummary]:
    try:
        return service.list_api_keys(access_key)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post(
    "/",
    response_model=ApiKeyCreateResponse,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "valid_until must be in the future.",
        },
    },
)
async def create_api_key(
    request: ApiKeyCreateRequest,
    actor_id: str = Depends(get_audit_actor),
    service: ApiKeysService = Depends(ApiKeysService),
) -> ApiKeyCreateResponse:
    try:
        return service.create_api_key(actor_id, request)
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete(
    "/{access_key}",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "API key not found.",
        },
    },
)
async def delete_api_key(
    access_key: str,
    actor_id: str = Depends(get_audit_actor),
    service: ApiKeysService = Depends(ApiKeysService),
) -> None:
    try:
        service.delete_api_key(actor_id, access_key)
    except ServiceError as err:
        raise_http_from_service_error(err)
