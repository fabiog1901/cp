from fastapi import APIRouter, Security

from ...auth import require_admin
from ...cpkit_integration import create_admin_router
from . import (
    cpu_counts,
    database_role_templates,
    disk_sizes,
    node_counts,
    regions,
    versions,
)

router = APIRouter(
    prefix="/admin",
    dependencies=[Security(require_admin)],
)

router.include_router(create_admin_router())
router.include_router(versions.router)
router.include_router(node_counts.router)
router.include_router(cpu_counts.router)
router.include_router(disk_sizes.router)
router.include_router(database_role_templates.router)
router.include_router(regions.router)
