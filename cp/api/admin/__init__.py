from fastapi import APIRouter, Security

from cpkit.auth import create_api_keys_router
from cpkit.playbooks import create_playbooks_router
from cpkit.settings import create_settings_router

from ...auth import require_admin
from ...auth import get_audit_actor
from . import (
    cpu_counts,
    database_role_templates,
    disk_sizes,
    node_counts,
    regions,
    versions,
)
from ...infra import get_api_keys_service, get_playbooks_service, get_settings_service
from ...services.errors import ServiceError
from .common import raise_http_from_service_error

router = APIRouter(
    prefix="/admin",
    dependencies=[Security(require_admin)],
)

router.include_router(
    create_settings_router(
        get_service=get_settings_service,
        get_audit_actor=get_audit_actor,
        handle_service_error=raise_http_from_service_error,
        service_error_type=ServiceError,
    )
)
router.include_router(versions.router)
router.include_router(node_counts.router)
router.include_router(cpu_counts.router)
router.include_router(disk_sizes.router)
router.include_router(database_role_templates.router)
router.include_router(regions.router)
router.include_router(
    create_playbooks_router(
        get_service=get_playbooks_service,
        get_audit_actor=get_audit_actor,
        handle_service_error=raise_http_from_service_error,
        service_error_type=ServiceError,
    )
)
router.include_router(
    create_api_keys_router(
        get_service=get_api_keys_service,
        get_audit_actor=get_audit_actor,
        handle_service_error=raise_http_from_service_error,
        service_error_type=ServiceError,
    )
)
