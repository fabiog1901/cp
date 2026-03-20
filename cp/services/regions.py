"""Business logic for the regions vertical."""

import json
from typing import Any

from ..models import EventType, Region
from ..repos.postgres import events, regions


def list_regions() -> list[Region]:
    return regions.list_regions()


def delete_region(region: Region, deleted_by: str) -> None:
    regions.delete_region(region.cloud, region.region, region.zone)
    events.insert_event_log(
        deleted_by,
        EventType.REGION_REMOVE,
        {"cloud": region.cloud, "region": region.region, "zone": region.zone},
    )


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
    extras = _parse_extras(extras_text)

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

    regions.add_region(new_region)
    events.insert_event_log(
        created_by,
        EventType.REGION_ADD,
        new_region.model_dump_json(),
    )
    return new_region


def _parse_extras(extras_text: str) -> dict[str, Any]:
    if not extras_text.strip():
        return {}

    parsed = json.loads(extras_text)
    if not isinstance(parsed, dict):
        raise ValueError("extras must be a JSON object")
    return parsed
