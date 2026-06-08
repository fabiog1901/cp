"""Admin API keys repository."""

from cpkit.auth import APIKeysRepositoryMixin

from ...models import ApiKeyRecord, ApiKeySummary
from .base import AdminRepo


class ApiKeysRepo(APIKeysRepositoryMixin, AdminRepo):
    api_key_record_type = ApiKeyRecord
    api_key_summary_type = ApiKeySummary
