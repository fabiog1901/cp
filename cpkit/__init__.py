"""Development import shim for the in-repo cpkit package."""

from pathlib import Path

_package_dir = Path(__file__).parent / "cpkit"
if _package_dir.is_dir():
    __path__.append(str(_package_dir))
