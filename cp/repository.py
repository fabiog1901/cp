"""CP repository factory and application-specific database error handling."""

from cpkit.db import get_pool
from cpkit.db import translate_database_error as _translate_database_error

from .cluster_database import ClusterDatabaseConnectionError


def get_repo():
    from .repos import Repo

    return Repo(get_pool())


def translate_database_error(err: Exception, operation: str | None):
    return _translate_database_error(
        err,
        operation,
        unavailable_error_types=(ClusterDatabaseConnectionError,),
    )
