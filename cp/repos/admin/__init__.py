"""Admin repository package."""

from .api_keys import ApiKeysRepo
from .base import AdminRepo
from .cluster_options import ClusterOptionsRepo
from .playbooks import PlaybooksRepo
from .regions import RegionsRepo
from .settings import SettingsRepo
from .versions import VersionsRepo

__all__ = [
    "AdminRepo",
    "ApiKeysRepo",
    "ClusterOptionsRepo",
    "PlaybooksRepo",
    "RegionsRepo",
    "SettingsRepo",
    "VersionsRepo",
]
