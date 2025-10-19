import asyncio

import reflex as rx
import time
import requests, time
from typing import Any
import datetime as dt

from ...backend import db
from ...components.main import cluster_banner, mini_breadcrumb
from ...cp import app
from ...models import Cluster, Job, STRFTIME
from ...state import AuthState
from ...template import template

ROUTE = "/clusters/[c_id]/dashboard"


def merge_by_ts(named_series: dict[str, dict[int, float]]):
    """Merge multiple {name -> {ts->val}} dicts into a list of rows."""
    # Collect all timestamps
    all_ts = sorted({ts for series in named_series.values() for ts in series.keys()})
    rows = []
    for ts in all_ts:
        row = {"ts": ts}
        for name, series in named_series.items():
            if ts in series:
                row[name] = series[ts]
        rows.append(row)
    return rows


class State(AuthState):
    current_cluster: Cluster = None

    # charts
    prom_url: str = ""
    period_mins: int = 30
    start: int = 0
    end: int = 0
    interval_secs = 10

    cpu_util_data: list[dict[str, Any]] = []
    stmt_data: list[dict[str, Any]] = []

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

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

                self.end = int(time.time())

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
                new_data = [
                    {
                        "ts": dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime(
                            STRFTIME,
                        ),
                        "cpu_util": round(float(val), 2) * 100,
                    }
                    for ts, val in r.json()["data"]["result"][0]["values"]
                ]

                # roll in newer datapoints
                self.cpu_util_data = self.cpu_util_data[len(new_data) :] + new_data

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
                select_series = {}

                for ts, val in r.json()["data"]["result"][0]["values"]:

                    select_series[
                        dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime(
                            STRFTIME,
                        )
                    ] = round(float(val), 2)

                # roll in newer datapoints
                # self.selects_data = self.selects_data[len(new_data) :] + new_data

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

                update_series = {}

                for ts, val in r.json()["data"]["result"][0]["values"]:
                    update_series[
                        dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime(
                            STRFTIME,
                        )
                    ] = round(float(val), 2)


                new_data = merge_by_ts(
                    {
                        "s": select_series,
                        "u": update_series,
                    }
                )
                
                print(new_data)

                # roll in newer datapoints
                self.stmt_data = self.stmt_data[len(new_data) :] + new_data

                self.start = 0

            await asyncio.sleep(10)


def cpu_util():
    return (
        rx.vstack(
            rx.heading("CPU Util"),
            rx.recharts.line_chart(
                rx.recharts.line(
                    data_key="cpu_util",
                    # type_="monotone",
                    stroke="#8884d8",
                    dot=False,
                    is_animation_active=False,
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


def sql_queries_per_second():
    return rx.vstack(
        rx.heading("SQL Queries per Second"),
        rx.recharts.line_chart(
            rx.recharts.line(
                name="selects",
                data_key="s",
                # type_="monotone",
                stroke="#8884d8",
                dot=False,
                is_animation_active=False,
            ),
            rx.recharts.line(
                name="updates",
                data_key="u",
                # type_="monotone",
                stroke="#82ca9d",
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


@rx.page(
    route=ROUTE,
    title=f"Cluster {State.current_cluster.cluster_id}: Jobs",
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
            rx.flex(
                mini_breadcrumb(
                    State.cluster_id, f"/clusters/{State.cluster_id}", "Jobs"
                ),
                cpu_util(),
                sql_queries_per_second(),
                class_name="flex-1 flex-col overflow-hidden",
            ),
            class_name="flex-1 pt-8 overflow-hidden",
        ),
        class_name="flex-col flex-1 overflow-hidden",
        on_mount=State.start_bg_event,
    )
