"""Admin playbooks repository."""

from cpkit.playbooks import PlaybooksRepositoryMixin

from .base import AdminRepo


class PlaybooksRepo(PlaybooksRepositoryMixin, AdminRepo):
    pass
