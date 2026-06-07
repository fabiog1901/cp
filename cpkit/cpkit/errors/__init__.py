"""Shared framework exception types."""

from .repository import (
    RepositoryConflictError,
    RepositoryError,
    RepositoryPermissionError,
    RepositoryUnavailableError,
    RepositoryValidationError,
)
from .service import (
    ServiceAuthorizationError,
    ServiceConflictError,
    ServiceError,
    ServiceNotFoundError,
    ServiceUnavailableError,
    ServiceValidationError,
    from_repository_error,
)

__all__ = [
    "RepositoryConflictError",
    "RepositoryError",
    "RepositoryPermissionError",
    "RepositoryUnavailableError",
    "RepositoryValidationError",
    "ServiceAuthorizationError",
    "ServiceConflictError",
    "ServiceError",
    "ServiceNotFoundError",
    "ServiceUnavailableError",
    "ServiceValidationError",
    "from_repository_error",
]
