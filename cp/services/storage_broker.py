"""Provision and resolve external storage connections for clusters."""

import datetime as dt
import json
import secrets
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, urlencode

from cpkit.auth import decrypt_secret, encrypt_secret

from ..repository import get_repo
from ..models import ExternalConnection, ExternalConnectionUpsert, SettingKey
from ..repos import Repo
from cpkit.errors import ServiceValidationError

BACKUP_CONNECTION_NAME = "backup"
BACKUP_CONNECTION_TYPE = "s3"
BACKUP_PROVIDER = "s3"
BACKUP_CONNECTION_STATUS_READY = "READY"
S3_REGION = "us-east-1"


@dataclass(frozen=True)
class PresignedS3Url:
    url: str
    bucket: str
    object_key: str
    expires_at: dt.datetime


class StorageBrokerService:
    def __init__(self, repo: Repo | None = None) -> None:
        self.repo = repo or get_repo()

    def create_bucket_service_account(
        self, bucketname: str, access_key: str, secret_key: str
    ):
        """
        Temporary fix until rustfs has a stable API.
        """

        policy_path = "/tmp/rustfspolicy.json"

        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": [f"arn:aws:s3:::{bucketname}"],
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:*"],
                    "Resource": [f"arn:aws:s3:::{bucketname}/*"],
                },
            ],
        }
        Path(policy_path).write_text(json.dumps(policy_document, indent=2) + "\n")

        subprocess.run(
            ["rc", "mb", f"rem/{bucketname}"],
            check=True,
            text=True,
        )
        subprocess.run(
            [
                "rc",
                "admin",
                "policy",
                "create",
                "rem",
                f"{bucketname}-policy",
                str(policy_path),
            ],
            check=True,
            text=True,
        )

        subprocess.run(
            [
                "rc",
                "admin",
                "service-account",
                "create",
                "rem",
                access_key,
                secret_key,
                "--policy",
                policy_path,
                "--name",
                f"{bucketname}-sa",
            ],
            check=True,
            text=True,
        )

    def ensure_backup_external_connection(
        self,
        cluster_id: str,
        created_by: str,
    ) -> ExternalConnection:
        existing = self.repo.get_external_connection(cluster_id, BACKUP_CONNECTION_NAME)
        if existing is not None:
            return existing

        endpoint = self._get_required_setting(SettingKey.storage_s3_url)
        # admin_access_key = self._get_required_setting(
        #     SettingKey.storage_s3_admin_access_key
        # )
        # admin_secret_key = self._get_required_setting(
        #     SettingKey.storage_s3_admin_secret_key
        # )
        retention_days_raw = self._get_optional_setting(
            SettingKey.storage_s3_default_retention_days
        )
        retention_days = int(retention_days_raw) if retention_days_raw else None
        if retention_days is not None and retention_days < 1:
            raise ServiceValidationError(
                "storage.s3.default_retention_days must be greater than zero."
            )

        # parsed_endpoint = urlparse(endpoint)
        # minio_endpoint = parsed_endpoint.netloc or parsed_endpoint.path
        # if not minio_endpoint:
        #     raise ServiceValidationError(f"Invalid S3 endpoint '{endpoint}'.")

        # client = minio.Minio(
        #     minio_endpoint,
        #     access_key=admin_access_key,
        #     secret_key=admin_secret_key,
        #     secure=parsed_endpoint.scheme == "https",
        # )

        access_key_id = secrets.token_urlsafe(40)[:20]
        secret_access_key = secrets.token_urlsafe(40)[:20]

        # policy_name = f"cluster-{cluster_id}-backup"

        # policy_document = {
        #     "Version": "2012-10-17",
        #     "Statement": [
        #         {
        #             "Effect": "Allow",
        #             "Action": ["s3:*"],
        #             "Resource": [bucket_arn, f"{bucket_arn}/*"],
        #         }
        #     ],
        # }
        # policy_json = json.dumps(policy_document)

        # if not client.bucket_exists(bucket_name):
        #     client.make_bucket(bucket_name)

        # client.set_bucket_policy(bucket_name, policy_json)

        # if retention_days:
        #     client.set_bucket_lifecycle(
        #         bucket_name,
        #         LifecycleConfig(
        #             [
        #                 Rule(
        #                     status=ENABLED,
        #                     expiration=Expiration(days=retention_days),
        #                     rule_filter=Filter(),
        #                     rule_id=f"expire-{bucket_name}",
        #                 )
        #             ]
        #         ),
        #     )

        # for method_name, args, action in (
        #     (
        #         "add_canned_policy",
        #         (policy_name, policy_json),
        #         "policy creation",
        #     ),
        #     (
        #         "add_user",
        #         (access_key_id, secret_access_key),
        #         "user creation",
        #     ),
        #     (
        #         "set_policy",
        #         (policy_name, access_key_id),
        #         "policy attachment",
        #     ),
        # ):
        #     method = getattr(client, method_name, None)
        #     if method is None:
        #         raise RuntimeError(
        #             f"The installed minio client does not support {action} via '{method_name}'."
        #         )
        #     try:
        #         method(*args)
        #     except Exception as err:
        #         if method_name in {"add_canned_policy", "add_user"}:
        #             message = str(err).lower()
        #             if "exists" in message or "already" in message:
        #                 continue
        #         raise RuntimeError(
        #             f"Unable to provision S3 {action} using '{method_name}': {err}"
        #         ) from err

        # this is a temp fix until rustfs has a stable admin API
        self.create_bucket_service_account(cluster_id, access_key_id, secret_access_key)

        connection = ExternalConnectionUpsert(
            cluster_id=cluster_id,
            name=BACKUP_CONNECTION_NAME,
            connection_type=BACKUP_CONNECTION_TYPE,
            provider=BACKUP_PROVIDER,
            endpoint=endpoint,
            bucket_name=cluster_id,
            access_key_id=access_key_id,
            encrypted_secret_access_key=encrypt_secret(secret_access_key),
            metadata={
                "policy_name": f"{cluster_id}-policy",
                "retention_days": retention_days,
                "s3_addressing_style": "path",
            },
            status=BACKUP_CONNECTION_STATUS_READY,
        )
        self.repo.upsert_external_connection(connection, updated_by=created_by)

        created = self.repo.get_external_connection(cluster_id, BACKUP_CONNECTION_NAME)
        if created is None:
            raise RuntimeError("Backup external connection was not persisted.")
        return created

    def get_backup_external_connection_uri(self, cluster_id: str) -> str:
        connection = self.repo.get_external_connection(
            cluster_id, BACKUP_CONNECTION_NAME
        )
        if connection is None:
            raise ServiceValidationError(
                f"Cluster '{cluster_id}' has no backup external connection configured."
            )
        return self.render_external_connection_uri(connection)

    def render_external_connection_uri(self, connection: ExternalConnection) -> str:
        if connection.connection_type.lower() != BACKUP_CONNECTION_TYPE:
            raise ServiceValidationError(
                f"Unsupported external connection type '{connection.connection_type}'."
            )
        if not connection.bucket_name:
            raise ServiceValidationError("External connection is missing bucket_name.")
        if not connection.access_key_id:
            raise ServiceValidationError(
                "External connection is missing access_key_id."
            )
        if not connection.encrypted_secret_access_key:
            raise ServiceValidationError(
                "External connection is missing encrypted_secret_access_key."
            )

        secret = decrypt_secret(connection.encrypted_secret_access_key).decode("utf-8")
        query = urlencode(
            {
                "AWS_ACCESS_KEY_ID": connection.access_key_id,
                "AWS_SECRET_ACCESS_KEY": secret,
                "AWS_REGION": "us-east-1",
            },
            quote_via=quote,
            safe="",
        )
        return (
            f"s3://{connection.bucket_name}?{query}&AWS_ENDPOINT={connection.endpoint}"
        )

    def create_presigned_put_url(
        self,
        cluster_id: str,
        object_key: str,
        *,
        created_by: str = "system",
        expires_seconds: int = 86400,
    ) -> PresignedS3Url:
        return self._create_presigned_url(
            "put_object",
            cluster_id,
            object_key,
            created_by=created_by,
            expires_seconds=expires_seconds,
        )

    def create_presigned_get_url(
        self,
        cluster_id: str,
        object_key: str,
        *,
        expires_seconds: int = 3600,
    ) -> PresignedS3Url:
        return self._create_presigned_url(
            "get_object",
            cluster_id,
            object_key,
            expires_seconds=expires_seconds,
        )

    def _create_presigned_url(
        self,
        client_method: str,
        cluster_id: str,
        object_key: str,
        *,
        created_by: str = "system",
        expires_seconds: int,
    ) -> PresignedS3Url:
        if not object_key.strip():
            raise ServiceValidationError("Presigned S3 object key must not be empty.")
        if expires_seconds < 1 or expires_seconds > 604800:
            raise ServiceValidationError(
                "Presigned S3 URL expiry must be between 1 and 604800 seconds."
            )

        connection = self.ensure_backup_external_connection(cluster_id, created_by)
        if not connection.bucket_name:
            raise ServiceValidationError("External connection is missing bucket_name.")
        if not connection.access_key_id:
            raise ServiceValidationError(
                "External connection is missing access_key_id."
            )
        if not connection.encrypted_secret_access_key:
            raise ServiceValidationError(
                "External connection is missing encrypted_secret_access_key."
            )

        secret = decrypt_secret(connection.encrypted_secret_access_key).decode("utf-8")
        now = dt.datetime.now(dt.timezone.utc)
        expires_at = now + dt.timedelta(seconds=expires_seconds)
        s3 = self._s3_client(
            endpoint=connection.endpoint,
            access_key=connection.access_key_id,
            secret_key=secret,
        )
        return PresignedS3Url(
            url=s3.generate_presigned_url(
                client_method,
                Params={
                    "Bucket": connection.bucket_name,
                    "Key": object_key,
                },
                ExpiresIn=expires_seconds,
            ),
            bucket=connection.bucket_name,
            object_key=object_key,
            expires_at=expires_at,
        )

    def _s3_client(
        self,
        *,
        endpoint: str,
        access_key: str,
        secret_key: str,
    ):
        try:
            import boto3
            from botocore.client import Config
        except ImportError as err:
            raise ServiceValidationError(
                "boto3 is required to generate presigned S3 URLs."
            ) from err

        return boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=S3_REGION,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
            ),
        )

    def _get_required_setting(self, key: SettingKey) -> str:
        setting = self.repo.get_setting(key)
        if setting is None or not setting.value:
            raise ServiceValidationError(f"Required setting '{key}' is not configured.")
        return setting.value.strip()

    def _get_optional_setting(self, key: SettingKey) -> str | None:
        setting = self.repo.get_setting(key)
        if setting is None or not setting.value:
            return None
        return setting.value.strip()
