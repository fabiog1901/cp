"""Reusable API-key request signing helpers."""

from datetime import datetime, timezone
from hashlib import sha256
from hmac import new as hmac_new
from typing import Any


def parse_api_key_timestamp(timestamp: str) -> datetime:
    """Parse either epoch seconds or an ISO-8601 timestamp into UTC."""
    raw_timestamp = timestamp.strip()
    if not raw_timestamp:
        raise ValueError("empty timestamp")

    try:
        parsed = datetime.fromtimestamp(float(raw_timestamp), tz=timezone.utc)
    except (OSError, OverflowError, ValueError):
        normalized = (
            f"{raw_timestamp[:-1]}+00:00"
            if raw_timestamp.endswith("Z")
            else raw_timestamp
        )
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        else:
            parsed = parsed.astimezone(timezone.utc)

    return parsed


def request_target_bytes(request: Any) -> bytes:
    """Return the exact path and query bytes covered by the request signature."""
    raw_path = request.scope.get("raw_path")
    if isinstance(raw_path, bytes) and raw_path:
        path = raw_path
    else:
        path = request.url.path.encode("utf-8")

    query_string = request.scope.get("query_string")
    if isinstance(query_string, bytes) and query_string:
        return path + b"?" + query_string
    return path


def build_api_key_signature_payload(
    request: Any,
    timestamp: str,
    body: bytes,
) -> bytes:
    """Build the canonical payload used for HMAC request signing."""
    return b"\n".join(
        [
            request.method.upper().encode("utf-8"),
            request_target_bytes(request),
            timestamp.strip().encode("utf-8"),
            body,
        ]
    )


def api_key_signature(
    secret_key: bytes,
    request: Any,
    timestamp: str,
    body: bytes,
) -> str:
    """Return the expected HMAC signature for an API-key-authenticated request."""
    return hmac_new(
        secret_key,
        build_api_key_signature_payload(request, timestamp, body),
        sha256,
    ).hexdigest()
