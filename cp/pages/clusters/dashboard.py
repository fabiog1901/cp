import asyncio
import time
from typing import Any

import reflex as rx
import requests

from ...backend import db
from ...components.main import cluster_banner, mini_breadcrumb
from ...cp import app
from ...models import STRFTIME, Cluster
from ...state import AuthState
from ...template import template

ROUTE = "/clusters/[c_id]/dashboard"


def merge_by_ts(named_series: dict[str, dict[int, float]]):
    """Merge multiple {name -> {ts->val}} dicts into a list of rows."""
    # Collect all timestamps
    all_ts = sorted(
        set({ts for series in named_series.values() for ts in series.keys()})
    )

    rows = []
    for ts in all_ts:
        row = {
            "ts": time.strftime(STRFTIME, time.gmtime(ts)),
            "t": 0,
        }
        for name, series in named_series.items():
            if ts in series:
                row[name] = series[ts]
                row["t"] += series[ts]

        rows.append(row)
    return rows


class State(AuthState):
    current_cluster: Cluster = None
    current_nodes: list[list[int, str]] = []

    # charts
    prom_url: str = ""
    period_mins: int = 30
    start: int = 0
    end: int = 0
    interval_secs = 10

    cpu_util_data: list[dict[str, Any]] = []
    stmt_data: list[dict[str, Any]] = []
    service_latency_data: list[dict[str, Any]] = []

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

    colors = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
        "#393b79",
        "#637939",
        "#8c6d31",
        "#843c39",
        "#7b4173",
        "#3182bd",
        "#31a354",
        "#756bb1",
        "#636363",
        "#969696",
    ]

    strokes = [None, "2 2 ", "5 5", "10 5"]

    is_running: bool = False

    @rx.event(background=True)
    async def start_bg_event(self):
        if self.is_running:
            return
        async with self:
            self.is_running = True

            self.prom_url = db.get_setting("prom_url")
            self.start = int(time.time()) - 60 * self.period_mins

        while True:
            if (
                self.router.page.path != ROUTE
                or self.router.session.client_token
                not in app.event_namespace.token_to_sid
            ):
                print(f"{ROUTE}: Stopping background task.")
                async with self:
                    self.is_running = False
                    self.cpu_util_data = []
                    self.stmt_data = []
                    self.service_latency_data = []
                break

            async with self:
                cluster: Cluster = db.get_cluster(
                    self.cluster_id,
                    list(self.webuser.groups),
                    self.is_admin,
                )
                if cluster is None:
                    self.is_running = False
                    return rx.redirect("/_notfound", replace=True)

                self.current_cluster = cluster
                self.current_nodes = []

                self.end = int(time.time())

                # SERVICE LATENCY P99
                r = requests.get(
                    self.prom_url,
                    params={
                        "query": f'histogram_quantile(0.99, rate(sql_service_latency_bucket{{cluster="{self.cluster_id}"}}[1m])) / 1000 / 1000',
                        "start": self.start if self.start > 0 else self.end,
                        "end": self.end,
                        "step": f"{self.interval_secs}s",
                    },
                )
                r.raise_for_status()

                new_data = [
                    {
                        "ts": ts,
                        "v": round(float(v), 2),
                    }
                    for ts, v in r.json()["data"]["result"][0]["values"]
                ]

                p99 = {}
                for idx, item in enumerate(r.json()["data"]["result"]):

                    self.current_nodes.append([idx, f"n{item['metric']['node_id']}"])

                    p99[f"n{item['metric']['node_id']}"] = {
                        ts: round(float(v), 2) for ts, v in item["values"]
                    }

                new_data = merge_by_ts(p99)

                # roll in newer datapoints
                self.service_latency_data = (
                    self.service_latency_data[len(new_data) :] + new_data
                )

                # CPU UTIL
                r = requests.get(
                    self.prom_url,
                    params={
                        "query": f'sys_cpu_user_percent{{cluster="{self.cluster_id}"}}',
                        "start": self.start if self.start > 0 else self.end,
                        "end": self.end,
                        "step": f"{self.interval_secs}s",
                    },
                )
                r.raise_for_status()

                cpu_utils = {}
                for idx, item in enumerate(r.json()["data"]["result"]):
                    cpu_utils[f"n{item['metric']['node_id']}"] = {
                        ts: round(float(v) * 100, 2) for ts, v in item["values"]
                    }

                new_data = merge_by_ts(cpu_utils)

                # roll in newer datapoints
                self.cpu_util_data = self.cpu_util_data[len(new_data) :] + new_data

                # SQL STATEMENTS
                r = requests.get(
                    self.prom_url,
                    params={
                        "query": f'sum(rate(sql_select_count{{cluster="{self.cluster_id}"}}[1m]))',
                        "start": self.start if self.start > 0 else self.end,
                        "end": self.end,
                        "step": f"{self.interval_secs}s",
                    },
                )
                r.raise_for_status()
                select_series = {
                    ts: round(float(v), 2)
                    for ts, v in r.json()["data"]["result"][0]["values"]
                }

                r = requests.get(
                    self.prom_url,
                    params={
                        "query": f'sum(rate(sql_insert_count{{cluster="{self.cluster_id}"}}[1m]))',
                        "start": self.start if self.start > 0 else self.end,
                        "end": self.end,
                        "step": f"{self.interval_secs}s",
                    },
                )
                r.raise_for_status()
                insert_series = {
                    ts: round(float(v), 2)
                    for ts, v in r.json()["data"]["result"][0]["values"]
                }

                r = requests.get(
                    self.prom_url,
                    params={
                        "query": f'sum(rate(sql_update_count{{cluster="{self.cluster_id}"}}[1m]))',
                        "start": self.start if self.start > 0 else self.end,
                        "end": self.end,
                        "step": f"{self.interval_secs}s",
                    },
                )
                r.raise_for_status()
                update_series = {
                    ts: round(float(v), 2)
                    for ts, v in r.json()["data"]["result"][0]["values"]
                }

                r = requests.get(
                    self.prom_url,
                    params={
                        "query": f'sum(rate(sql_delete_count{{cluster="{self.cluster_id}"}}[1m]))',
                        "start": self.start if self.start > 0 else self.end,
                        "end": self.end,
                        "step": f"{self.interval_secs}s",
                    },
                )
                r.raise_for_status()
                delete_series = {
                    ts: round(float(v), 2)
                    for ts, v in r.json()["data"]["result"][0]["values"]
                }

                new_data = merge_by_ts(
                    {
                        "s": select_series,
                        "i": insert_series,
                        "u": update_series,
                        "d": delete_series,
                    }
                )

                # roll in newer datapoints
                self.stmt_data = self.stmt_data[len(new_data) :] + new_data

                self.start = 0

            await asyncio.sleep(10)


def chart_cpu_util():
    return (
        rx.vstack(
            rx.heading("CPU Util"),
            rx.recharts.line_chart(
                rx.foreach(
                    State.current_nodes,
                    lambda x: rx.recharts.line(
                        data_key=x[1],
                        # type_="monotone",
                        stroke=State.colors[x[0] % 20],
                        dot=False,
                        stroke_dasharray=State.strokes[x[0] // 20 % 4],
                        stroke_width=x[0] // 80 + 1,
                        is_animation_active=False,
                    ),
                ),
                rx.recharts.x_axis(data_key="ts"),
                rx.recharts.y_axis(
                    label={
                        "value": "CPU Util (%)",
                        "angle": -90,  # rotate vertically
                        "position": "insideLeft",  # or "insideRight", "outsideLeft", etc.
                    }
                ),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                data=State.cpu_util_data,
                width="100%",
                height=300,
            ),
            align="center",
        ),
    )


def chart_sql_queries_per_second():
    return rx.vstack(
        rx.heading("SQL Queries per Second"),
        rx.recharts.line_chart(
            rx.recharts.line(
                name="selects",
                data_key="s",
                # type_="monotone",
                stroke="#495eff",
                dot=False,
                is_animation_active=False,
            ),
            rx.recharts.line(
                name="updates",
                data_key="u",
                # type_="monotone",
                stroke="#CE8943",
                dot=False,
                is_animation_active=False,
            ),
            rx.recharts.line(
                name="deletes",
                data_key="d",
                # type_="monotone",
                stroke="#d20f0f",
                dot=False,
                is_animation_active=False,
            ),
            rx.recharts.line(
                name="inserts",
                data_key="i",
                # type_="monotone",
                stroke="#F68EFF",
                dot=False,
                is_animation_active=False,
            ),
            rx.recharts.line(
                name="total",
                data_key="t",
                # type_="monotone",
                stroke="#FFFFFF",
                dot=False,
                is_animation_active=False,
            ),
            rx.recharts.x_axis(data_key="ts"),
            rx.recharts.y_axis(
                label={
                    "value": "queries",
                    "angle": -90,  # rotate vertically
                    "position": "insideLeft",  # or "insideRight", "outsideLeft", etc.
                }
            ),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            rx.recharts.legend(),
            data=State.stmt_data,
            width="100%",
            height=300,
        ),
        align="center",
        spacing="3",
    )


def chart_service_latency():
    return (
        rx.vstack(
            rx.heading("Service Latency p99"),
            rx.recharts.line_chart(
                rx.foreach(
                    State.current_nodes,
                    lambda x: rx.recharts.line(
                        data_key=x[1],
                        # type_="monotone",
                        stroke=State.colors[x[0] % 20],
                        dot=False,
                        stroke_dasharray=State.strokes[x[0] // 20 % 4],
                        stroke_width=x[0] // 80 + 1,
                        is_animation_active=False,
                    ),
                ),
                rx.recharts.x_axis(data_key="ts"),
                rx.recharts.y_axis(
                    label={
                        "value": "latency (ms)",
                        "angle": -90,  # rotate vertically
                        "position": "insideLeft",  # or "insideRight", "outsideLeft", etc.
                    }
                ),
                rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                rx.recharts.graphing_tooltip(),
                rx.recharts.legend(),
                data=State.service_latency_data,
                width="100%",
                height=300,
            ),
            align="center",
        ),
    )


@rx.page(
    route=ROUTE,
    title=f"{State.current_cluster.cluster_id} Dashboard",
    on_load=AuthState.check_login,
)
@template
def webpage():
    return rx.flex(
        cluster_banner(
            "boxes",
            State.current_cluster.cluster_id,
            State.current_cluster.status,
            State.current_cluster.version,
        ),
        rx.flex(
            mini_breadcrumb(
                State.cluster_id, f"/clusters/{State.cluster_id}", "Dashboard"
            ),
            rx.flex(
                chart_cpu_util(),
                chart_sql_queries_per_second(),
                chart_service_latency(),
                class_name="flex-1 flex-col overflow-y-scroll",
            ),
            class_name="flex-1 flex-col pt-8 overflow-hidden",
        ),
        class_name="flex-col flex-1 overflow-hidden",
        on_mount=State.start_bg_event,
    )
