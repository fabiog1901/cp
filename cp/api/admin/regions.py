import json

from fastapi import APIRouter, Depends

from ...auth import get_audit_actor
from ...infra import get_regions_service
from ...models import Region
from ...services.errors import ServiceError
from ...services.regions import RegionsService
from .common import raise_http_from_service_error

router = APIRouter(prefix="/regions", tags=["admin"])


@router.get("/")
async def list_regions(
    service: RegionsService = Depends(get_regions_service),
) -> list[Region]:
    try:
        return service.list_regions()
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.post("/")
async def create_region(
    request: Region,
    actor_id: str = Depends(get_audit_actor),
    service: RegionsService = Depends(get_regions_service),
) -> Region:
    try:
        return service.create_region(
            cloud=request.cloud,
            region=request.region,
            zone=request.zone,
            vpc_id=request.vpc_id,
            security_groups_text=",".join(request.security_groups),
            subnet=request.subnet,
            image=request.image,
            extras_text=json.dumps(request.extras),
            created_by=actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)


@router.delete("/{cloud}/{region}/{zone}")
async def delete_region(
    cloud: str,
    region: str,
    zone: str,
    actor_id: str = Depends(get_audit_actor),
    service: RegionsService = Depends(get_regions_service),
) -> None:
    try:
        service.delete_region(
            Region(
                cloud=cloud,
                region=region,
                zone=zone,
                vpc_id="",
                security_groups=[],
                subnet="",
                image="",
                extras={},
            ),
            actor_id,
        )
    except ServiceError as err:
        raise_http_from_service_error(err)
