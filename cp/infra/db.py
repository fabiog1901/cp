"""CP metadata database infrastructure adapter."""

import os

from cpkit.db import (
    close_db,
    execute_stmt,
    fetch_all,
    fetch_one,
    fetch_scalar,
    get_pool,
    initialize_postgres,
)
from cpkit.db import translate_database_error as _translate_database_error

from .util import ClusterDatabaseConnectionError

DB_URL = os.getenv("DB_URL")


def get_repo():
    from ..repos import Repo

    return Repo(get_pool())


def translate_database_error(err: Exception, operation: str | None):
    return _translate_database_error(
        err,
        operation,
        unavailable_error_types=(ClusterDatabaseConnectionError,),
    )


__all__ = [
    "DB_URL",
    "close_db",
    "execute_stmt",
    "fetch_all",
    "fetch_one",
    "fetch_scalar",
    "get_pool",
    "get_repo",
    "initialize_postgres",
    "translate_database_error",
]
