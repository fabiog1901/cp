"""Development import shim for the in-repo cpkit package."""

from pathlib import Path

_package_dir = Path(__file__).parent / "cpkit"
if _package_dir.is_dir():
    __path__.append(str(_package_dir))

from .admin import create_cpkit_admin_router
from .app import create_cpkit_app
from .bundle import CpkitBundle, create_cpkit_bundle
from .repository import configure_repository, get_repo

__all__ = [
    "CpkitBundle",
    "configure_repository",
    "create_cpkit_bundle",
    "create_cpkit_admin_router",
    "create_cpkit_app",
    "get_repo",
]
