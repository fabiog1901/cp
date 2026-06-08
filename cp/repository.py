"""CP repository compatibility helpers."""

from cpkit import get_repo
from cpkit.db import translate_database_error as _translate_database_error

from .cluster_database import ClusterDatabaseConnectionError


def translate_database_error(err: Exception, operation: str | None):
    return _translate_database_error(
        err,
        operation,
        unavailable_error_types=(ClusterDatabaseConnectionError,),
    )
