from fastapi import APIRouter, Security

from ...auth import require_admin
from . import events, playbooks, regions, settings, versions

router = APIRouter(
    prefix="/admin",
    dependencies=[Security(require_admin)],
)

router.include_router(settings.router)
router.include_router(versions.router)
router.include_router(regions.router)
router.include_router(playbooks.router)
router.include_router(events.router)
