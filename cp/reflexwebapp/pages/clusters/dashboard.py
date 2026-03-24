import asyncio
import time
from typing import Any

import reflex as rx

from ....cp import app
from ....models import Cluster, DashboardSnapshot
from ....services.dashboard import DashboardService
from ...components.main import cluster_banner, mini_breadcrumb
from ...components.notify import NotifyState
from ...layouts.template import template
from ...state import AuthState

ROUTE = "/clusters/[c_id]/dashboard"


class State(AuthState):
    current_cluster: Cluster = None
    current_nodes: set[int] = set()

    # charts
    period_mins: int = 30
    start: int = 0
    end: int = 0
    interval_secs = 10

    chart_data: list[dict[str, Any]] = []

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

    is_running: bool = False

    @rx.event(background=True)
    async def start_bg_event(self):
        if self.is_running:
            return
        async with self:
            self.is_running = True
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
                    self.chart_data = []
                break

            async with self:
                self.end = int(time.time())
                try:
                    snapshot: DashboardSnapshot | None = (
                        DashboardService.load_dashboard_snapshot(
                            self.cluster_id,
                            list(self.webuser.groups),
                            self.is_admin,
                            self.start,
                            self.end,
                            self.interval_secs,
                        )
                    )
                except Exception as e:
                    self.is_running = False
                    return NotifyState.show("Error fetching dashboard", str(e))

                if snapshot is None:
                    self.is_running = False
                    return rx.redirect("/_notfound", replace=True)

                self.current_cluster = snapshot.cluster
                self.current_nodes = set(snapshot.metrics.current_nodes)
                new_data = snapshot.metrics.chart_data

                # roll in newer datapoints
                self.chart_data = self.chart_data[len(new_data) :] + new_data

                # by setting start=0, on the next iteration we only collect
                # the last data point
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
                        name=f"n{x}",
                        data_key=f"cpu_n{x}",
                        # type_="monotone",
                        stroke=State.colors[x % 20],
                        dot=False,
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
                data=State.chart_data,
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
            data=State.chart_data,
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
                        name=f"n{x}",
                        data_key=f"p99_n{x}",
                        # type_="monotone",
                        stroke=State.colors[x % 20],
                        dot=False,
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
                data=State.chart_data,
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
