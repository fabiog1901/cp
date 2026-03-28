import secrets
from datetime import datetime, timezone

from ..infra.errors import RepositoryError
from ..models import (
    ApiKeyCreateRequest,
    ApiKeyCreateRequestInDB,
    ApiKeyCreateResponse,
    ApiKeySummary,
    Event,
)
from ..infra.util import encrypt_api_key_secret
from ..repos.base import BaseRepo
from .base import log_event
from .errors import ServiceNotFoundError, ServiceValidationError, from_repository_error


class ApiKeysService:
    def __init__(self, repo: BaseRepo) -> None:
        self.repo = repo

    def list_api_keys(self, access_key: str | None = None) -> list[ApiKeySummary]:
        try:
            return self.repo.list_api_keys(access_key)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="API keys are temporarily unavailable.",
                fallback_message="Unable to load API keys.",
            ) from err

    def create_api_key(
        self,
        actor_id: str,
        request: ApiKeyCreateRequest,
    ) -> ApiKeyCreateResponse:

        valid_until = self._normalize_valid_until(request.valid_until)

        if valid_until <= datetime.now(timezone.utc):
            raise ServiceValidationError("valid_until must be in the future.")

        secret_access_key = secrets.token_urlsafe(32)

        access_key = "cp-" + secrets.token_urlsafe(16)

        try:
            created = self.repo.create_api_key(
                ApiKeyCreateRequestInDB(
                    access_key=access_key,
                    valid_until=valid_until,
                    roles=request.roles,
                ),
                owner=actor_id,
                encrypted_secret_access_key=encrypt_api_key_secret(secret_access_key),
            )
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="API keys could not be created right now.",
                conflict_message="That API key already exists.",
                validation_message="The API key request is invalid.",
                fallback_message="Unable to create API key.",
            ) from err

        log_event(
            self.repo,
            actor_id,
            action=Event.API_KEY_CREATE,
            details={
                "access_key": created.access_key,
                "valid_until": created.valid_until.isoformat(),
                "roles": [role.value for role in created.roles or []],
            },
        )

        return ApiKeyCreateResponse(
            access_key=created.access_key,
            owner=created.owner,
            valid_until=created.valid_until,
            roles=created.roles,
            secret_access_key=secret_access_key,
        )

    def delete_api_key(self, actor_id: str, access_key: str) -> None:
        try:
            existing_key = self.repo.get_api_key(access_key)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="API keys could not be updated right now.",
                fallback_message=f"Unable to load API key '{access_key}'.",
            ) from err

        if existing_key is None:
            raise ServiceNotFoundError("API key not found.")

        try:
            self.repo.delete_api_key(access_key)
        except RepositoryError as err:
            raise from_repository_error(
                err,
                unavailable_message="API keys could not be updated right now.",
                fallback_message=f"Unable to delete API key '{access_key}'.",
            ) from err

        log_event(
            self.repo,
            actor_id,
            action=Event.API_KEY_DELETE,
            details={
                "access_key": existing_key.access_key,
                "owner": existing_key.owner,
                "valid_until": existing_key.valid_until.isoformat(),
                "roles": [role.value for role in existing_key.roles or []],
            },
        )

    @staticmethod
    def _normalize_valid_until(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
