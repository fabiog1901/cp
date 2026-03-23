"""Dashboard infrastructure repository."""

import logging
from typing import Any

import requests

from ...infra.errors import RepositoryError, RepositoryUnavailableError

PROMETHEUS_TIMEOUT_SECS = 10
logger = logging.getLogger(__name__)

from ..base import BaseRepo

class DashboardRepo(BaseRepo):
    def query_prometheus_range(
        self,
        prom_url: str,
        *,
        query: str,
        start: int,
        end: int,
        interval_secs: int,
    ) -> dict[str, Any]:
        try:
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
        except requests.RequestException as err:
            logger.exception(
                "Prometheus query failed [operation=dashboard.query_prometheus_range]"
            )
            raise RepositoryUnavailableError(
                "Prometheus is temporarily unavailable.",
                operation="dashboard.query_prometheus_range",
                retryable=True,
            ) from err
        except ValueError as err:
            logger.exception(
                "Prometheus returned invalid JSON [operation=dashboard.query_prometheus_range]"
            )
            raise RepositoryError(
                "Prometheus returned an invalid response.",
                operation="dashboard.query_prometheus_range",
            ) from err
