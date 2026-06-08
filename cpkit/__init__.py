"""Development import shim for the in-repo cpkit package."""

from pathlib import Path

_package_dir = Path(__file__).parent / "cpkit"
if _package_dir.is_dir():
    __path__.append(str(_package_dir))

from .admin import create_cpkit_admin_router
from .app import create_cpkit_app

__all__ = [
    "create_cpkit_admin_router",
    "create_cpkit_app",
]
