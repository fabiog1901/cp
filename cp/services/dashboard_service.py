"""Business logic for the cluster dashboard vertical."""

import time
from typing import Any

import requests

from ..models import DashboardMetrics, DashboardSnapshot
from . import cluster_service, settings_service


PROMETHEUS_TIMEOUT_SECS = 10


def get_prometheus_url() -> str:
    prom_url = settings_service.get_setting("prom_url").strip()
    if not prom_url:
        raise ValueError("Missing Prometheus URL in settings.")
    return prom_url


def load_dashboard_snapshot(
    cluster_id: str,
    groups: list[str],
    is_admin: bool,
    start: int,
    end: int,
    interval_secs: int,
) -> DashboardSnapshot | None:
    cluster = cluster_service.get_cluster_for_user(cluster_id, groups, is_admin)
    if cluster is None:
        return None

    metrics = load_dashboard_metrics(
        get_prometheus_url(),
        cluster_id,
        start,
        end,
        interval_secs,
    )
    return DashboardSnapshot(cluster=cluster, metrics=metrics)


def load_dashboard_metrics(
    prom_url: str,
    cluster_id: str,
    start: int,
    end: int,
    interval_secs: int,
) -> DashboardMetrics:
    effective_start = start if start > 0 else end
    current_nodes: set[int] = set()
    series: dict[str, dict[int, float]] = {}

    for metric_name, query, transform, track_nodes in [
        (
            "latency",
            f'histogram_quantile(0.99, rate(sql_service_latency_bucket{{cluster="{cluster_id}"}}[1m])) / 1000 / 1000',
            lambda value: round(float(value), 2),
            True,
        ),
        (
            "cpu",
            f'sys_cpu_user_percent{{cluster="{cluster_id}"}}',
            lambda value: round(float(value) * 100, 2),
            True,
        ),
        (
            "selects",
            f'sum(rate(sql_select_count{{cluster="{cluster_id}"}}[1m]))',
            lambda value: round(float(value), 2),
            False,
        ),
        (
            "inserts",
            f'sum(rate(sql_insert_count{{cluster="{cluster_id}"}}[1m]))',
            lambda value: round(float(value), 2),
            False,
        ),
        (
            "updates",
            f'sum(rate(sql_update_count{{cluster="{cluster_id}"}}[1m]))',
            lambda value: round(float(value), 2),
            False,
        ),
        (
            "deletes",
            f'sum(rate(sql_delete_count{{cluster="{cluster_id}"}}[1m]))',
            lambda value: round(float(value), 2),
            False,
        ),
    ]:
        response = _query_prometheus(
            prom_url,
            query=query,
            start=effective_start,
            end=end,
            interval_secs=interval_secs,
        )

        if track_nodes:
            prefix = "p99" if metric_name == "latency" else "cpu"
            for item in response["data"]["result"]:
                node_id = int(item["metric"]["node_id"])
                current_nodes.add(node_id)
                series[f"{prefix}_n{node_id}"] = {
                    ts: transform(value) for ts, value in item["values"]
                }
            continue

        values = _first_result_values(response)
        series[metric_name[0]] = {ts: transform(value) for ts, value in values}

    return DashboardMetrics(
        current_nodes=sorted(current_nodes),
        chart_data=_merge_by_ts(series),
    )


def _query_prometheus(
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


def _first_result_values(response: dict[str, Any]) -> list[list[str | float]]:
    result = response.get("data", {}).get("result", [])
    if not result:
        return []
    return result[0].get("values", [])


def _merge_by_ts(named_series: dict[str, dict[int, float]]) -> list[dict[str, Any]]:
    if not named_series:
        return []

    all_ts = sorted(
        set({ts for series in named_series.values() for ts in series.keys()})
    )

    rows = []
    for ts in all_ts:
        row: dict[str, Any] = {"ts": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts))}
        for name, series in named_series.items():
            if ts in series:
                row[name] = series[ts]

        row["t"] = row.get("s", 0) + row.get("i", 0) + row.get("u", 0) + row.get("d", 0)
        rows.append(row)

    return rows
