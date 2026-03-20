"""Dashboard infrastructure repository."""

from typing import Any

import requests

PROMETHEUS_TIMEOUT_SECS = 10


def query_prometheus_range(
    prom_url: str,
    *,
    query: str,
    start: int,
    end: int,
    interval_secs: int,
) -> dict[str, Any]:
    response = requests.get(
        prom_url,
        params={
            "query": query,
            "start": start,
            "end": end,
            "step": f"{interval_secs}s",
        },
        timeout=PROMETHEUS_TIMEOUT_SECS,
    )
    response.raise_for_status()
    return response.json()
