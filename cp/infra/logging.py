"""CP logging configuration adapter."""

from cpkit.cpkit.logging import configure_logging as _configure_logging

from ..models import SettingKey


def configure_logging(repo=None, *, force: bool = False) -> None:
    """Configure app logging with CP's persisted logging settings."""
    _configure_logging(
        repo,
        force=force,
        default_journald_identifier="cp",
        level_key=SettingKey.logging_level,
        journald_identifier_key=SettingKey.logging_journald_identifier,
    )
