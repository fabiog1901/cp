"""Repository factory helpers for cpkit applications."""

from collections.abc import Callable
from typing import Any

from psycopg_pool import ConnectionPool

from cpkit.db import get_pool

RepoFactory = Callable[[], Any]
RepoClass = Callable[[ConnectionPool], Any]

_repo_factory: RepoFactory | None = None


def configure_repository(
    *,
    repo_class: RepoClass | None = None,
    repo_factory: RepoFactory | None = None,
) -> None:
    """Configure the application repository factory used by cpkit services."""
    global _repo_factory

    if repo_class is None and repo_factory is None:
        raise ValueError("repo_class or repo_factory is required.")
    if repo_class is not None and repo_factory is not None:
        raise ValueError("Pass only one of repo_class or repo_factory.")

    if repo_factory is not None:
        _repo_factory = repo_factory
        return

    assert repo_class is not None
    _repo_factory = lambda: repo_class(get_pool())


def get_repo() -> Any:
    """Return a repository instance for the configured cpkit application."""
    if _repo_factory is None:
        raise RuntimeError("Repository factory not configured.")
    return _repo_factory()
