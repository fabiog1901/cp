"""Application service facade.

This module is the single import point for the web layer and backend workers.
It currently delegates to the Cockroach/Postgres repository implementation so
we can migrate call sites incrementally without changing behavior.
"""

from ..repos.postgres import repository as repo

pool = repo.pool


def __getattr__(name: str):
    return getattr(repo, name)
