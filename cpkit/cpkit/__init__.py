"""Reusable control-plane framework primitives."""

from .admin import create_cpkit_admin_router
from .app import create_cpkit_app
from .bundle import CpkitBundle, create_cpkit_bundle
from .dependencies import (
    configure_cpkit_dependencies,
    get_access_scope,
    get_audit_actor,
    require_admin,
    require_authenticated,
    require_readonly,
    require_user,
)
from .repository import CPKitRepo, configure_repository, get_repo

__all__ = [
    "CPKitRepo",
    "CpkitBundle",
    "configure_cpkit_dependencies",
    "configure_repository",
    "create_cpkit_bundle",
    "create_cpkit_admin_router",
    "create_cpkit_app",
    "get_access_scope",
    "get_audit_actor",
    "get_repo",
    "require_admin",
    "require_authenticated",
    "require_readonly",
    "require_user",
]
