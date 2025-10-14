import asyncio

import reflex as rx

from ...backend import db
from ...components.BadgeClusterStatus import get_cluster_status_badge
from ...components.BadgeJobStatus import get_job_status_badge
from ...cp import app
from ...models import Cluster, Job
from ...state import AuthState
from ...template import template


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
                self.router.page.path != "/clusters/[c_id]/jobs"
                or self.router.session.client_token
                not in app.event_namespace.token_to_sid
            ):
                print("cluster_jobs.py: Stopping background task.")
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
                    # TODO redirect is buggy
                    return rx.redirect("/404", replace=True)

                self.current_cluster = cluster
                self.jobs = db.get_all_linked_jobs(self.cluster_id)
            await asyncio.sleep(5)


def get_job_row(job: Job):
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


def jobs_table():
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
                    get_job_row,
                )
            ),
            width="100%",
            size="3",
        ),
        rx.text(f"Showing {State.jobs.length()} jobs"),
        width="100%",
    )


@rx.page(
    route="/clusters/[c_id]/jobs",
    title=f"Cluster {State.current_cluster.cluster_id}: Jobs",
    on_load=AuthState.check_login,
)
@template
def webpage():
    return rx.flex(
        rx.hstack(
            rx.icon("boxes", size=100, class_name="p-2"),
            rx.text(
                State.current_cluster.cluster_id,
                class_name="p-2 text-8xl font-semibold",
            ),
            rx.divider(orientation="vertical", size="4", class_name="mx-8"),
            get_cluster_status_badge(State.current_cluster.status),
            rx.hstack(
                rx.vstack(
                    rx.text("Version"),
                    rx.text(
                        State.current_cluster.version,
                        class_name="text-3xl font-semibold",
                    ),
                    class_name="mx-16",
                    align="center",
                ),
                direction="row-reverse",
                class_name="p-4 flex-1",
            ),
            align="center",
        ),
        rx.flex(
            # cluster_sidebar(),
            rx.flex(
                rx.hstack(
                    rx.link(
                        rx.text(
                            State.cluster_id,
                            class_name="p-2 pt-2 font-semibold text-2xl",
                        ),
                        href=f"/clusters/{State.cluster_id}",
                    ),
                    rx.text(" > ", class_name="p-2 pt-2 font-semibold text-2xl"),
                    rx.text("Jobs", class_name="p-2 pt-2 font-semibold text-2xl"),
                    class_name="p-2",
                ),
                rx.flex(
                    jobs_table(),
                    class_name="flex-1 flex-col overflow-y-scroll p-2 pt-8",
                ),
                class_name="flex-1 flex-col overflow-hidden",
            ),
            class_name="flex-1 pt-8 overflow-hidden",
        ),
        class_name="flex-col flex-1 overflow-hidden",
        on_mount=State.start_bg_event,
    )
