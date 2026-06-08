"""CP auth dependency wiring."""

from cpkit.auth import (
    access_key_scheme,
    create_auth_dependencies,
    signature_scheme,
    timestamp_scheme,
)

from ..infra import get_repo
from ..models import CPRole
from .common import OIDC_SESSION_COOKIE_NAME
from .oidc import oidc

_auth_dependencies = create_auth_dependencies(
    oidc,
    get_repo=get_repo,
    session_cookie_name=OIDC_SESSION_COOKIE_NAME,
    readonly_roles=(CPRole.CP_READONLY,),
    user_roles=(CPRole.CP_USER, CPRole.CP_ADMIN),
    admin_roles=(CPRole.CP_ADMIN,),
)

require_authenticated = _auth_dependencies.require_authenticated
require_user = _auth_dependencies.require_user
require_readonly = _auth_dependencies.require_readonly
require_admin = _auth_dependencies.require_admin
get_access_scope = _auth_dependencies.get_access_scope
get_audit_actor = _auth_dependencies.get_audit_actor

__all__ = [
    "access_key_scheme",
    "get_access_scope",
    "get_audit_actor",
    "require_admin",
    "require_authenticated",
    "require_readonly",
    "require_user",
    "signature_scheme",
    "timestamp_scheme",
]
