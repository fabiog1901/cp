import asyncio

import reflex as rx

from ...backend import db
from ...components.BadgeJobStatus import get_job_status_badge
from ...components.main import cluster_banner, mini_breadcrumb
from ...cp import app
from ...models import Cluster, Job
from ...state import AuthState
from ...template import template
from ...components.notify import NotifyState

ROUTE = "/clusters/[c_id]/jobs"


class State(AuthState):
    current_cluster: Cluster = None
    jobs: list[Job] = []

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
                try:
                    cluster: Cluster = db.get_cluster(
                        self.cluster_id,
                        list(self.webuser.groups),
                        self.is_admin,
                    )
                except Exception as e:
                    self.is_running = False
                    return NotifyState.show("Error", str(e))

                if cluster is None:
                    self.is_running = False
                    return rx.redirect("/_notfound", replace=True)

                self.current_cluster = cluster

                try:
                    self.jobs = db.get_all_linked_jobs(self.cluster_id)
                except Exception as e:
                    self.is_running = False
                    return NotifyState.show("Error", str(e))

            await asyncio.sleep(5)


def table_row(job: Job):
    """Show a job in a table row."""
    return rx.table.row(
        rx.table.cell(
            rx.link(
                rx.text(job.job_id, class_name="text-2xl font-semibold"),
                href=f"/jobs/{job.job_id}",
            )
        ),
        rx.table.cell(job.job_type),
        rx.table.cell(job.created_by),
        rx.table.cell(get_job_status_badge(job.status)),
    )


def data_table():
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Job ID"),
                    rx.table.column_header_cell("Job Type"),
                    rx.table.column_header_cell("Created By"),
                    rx.table.column_header_cell("Status"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.jobs,
                    table_row,
                )
            ),
            width="100%",
            size="3",
        ),
        rx.text(f"Showing {State.jobs.length()} jobs"),
        width="100%",
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
                rx.flex(
                    data_table(),
                    class_name="flex-1 flex-col overflow-y-scroll p-2 pt-8",
                ),
                class_name="flex-1 flex-col overflow-hidden",
            ),
            class_name="flex-1 pt-8 overflow-hidden",
        ),
        class_name="flex-col flex-1 overflow-hidden",
        on_mount=State.start_bg_event,
    )
