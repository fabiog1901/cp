"""Compatibility exports for service-layer exception types."""

from cpkit.errors import (
    ServiceAuthorizationError,
    ServiceConflictError,
    ServiceError,
    ServiceNotFoundError,
    ServiceUnavailableError,
    ServiceValidationError,
    from_repository_error,
)

__all__ = [
    "ServiceAuthorizationError",
    "ServiceConflictError",
    "ServiceError",
    "ServiceNotFoundError",
    "ServiceUnavailableError",
    "ServiceValidationError",
    "from_repository_error",
]
