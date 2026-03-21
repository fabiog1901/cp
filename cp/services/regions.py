"""Business logic for the regions vertical."""

import json
from typing import Any

from ..infra.errors import RepositoryError
from ..models import EventType, Region
from ..repos.postgres import event_repo, regions_repo
from .errors import ServiceValidationError, from_repository_error


def list_regions() -> list[Region]:
    try:
        return regions_repo.list_regions()
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Regions are temporarily unavailable.",
            fallback_message="Unable to load regions_repo.",
        ) from err


def delete_region(region: Region, deleted_by: str) -> None:
    try:
        regions_repo.delete_region(region.cloud, region.region, region.zone)
        event_repo.insert_event_log(
            deleted_by,
            EventType.REGION_REMOVE,
            {"cloud": region.cloud, "region": region.region, "zone": region.zone},
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Region updates are temporarily unavailable.",
            fallback_message=f"Unable to delete region '{region.cloud}:{region.region}:{region.zone}'.",
        ) from err


def create_region(
    *,
    cloud: str,
    region: str,
    zone: str,
    vpc_id: str,
    security_groups_text: str,
    subnet: str,
    image: str,
    extras_text: str,
    created_by: str,
) -> Region:
    security_groups = [s.strip() for s in security_groups_text.split(",") if s.strip()]
    try:
        extras = _parse_extras(extras_text)
    except ValueError as err:
        raise ServiceValidationError(str(err)) from err

    new_region = Region(
        cloud=cloud,
        region=region,
        zone=zone,
        vpc_id=vpc_id,
        security_groups=security_groups,
        subnet=subnet,
        image=image,
        extras=extras,
    )

    try:
        regions_repo.add_region(new_region)
        event_repo.insert_event_log(
            created_by,
            EventType.REGION_ADD,
            new_region.model_dump_json(),
        )
    except RepositoryError as err:
        raise from_repository_error(
            err,
            unavailable_message="Region updates are temporarily unavailable.",
            conflict_message="That region already exists.",
            validation_message="The region details are invalid.",
            fallback_message=f"Unable to create region '{cloud}:{region}:{zone}'.",
        ) from err
    return new_region


def _parse_extras(extras_text: str) -> dict[str, Any]:
    if not extras_text.strip():
        return {}

    parsed = json.loads(extras_text)
    if not isinstance(parsed, dict):
        raise ServiceValidationError("extras must be a JSON object")
    return parsed
