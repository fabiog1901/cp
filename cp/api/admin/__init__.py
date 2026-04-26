from fastapi import APIRouter, Security

from ...auth import require_admin
from . import (
    api_keys,
    cpu_counts,
    database_roles,
    disk_sizes,
    node_counts,
    playbooks,
    regions,
    settings,
    versions,
)

router = APIRouter(
    prefix="/admin",
    dependencies=[Security(require_admin)],
)

router.include_router(settings.router)
router.include_router(versions.router)
router.include_router(node_counts.router)
router.include_router(cpu_counts.router)
router.include_router(disk_sizes.router)
router.include_router(database_roles.router)
router.include_router(regions.router)
router.include_router(playbooks.router)
router.include_router(api_keys.router)
