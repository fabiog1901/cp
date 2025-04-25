import reflex as rx
import asyncio

from ..template import template
from ..models import Cluster, ClusterOverview, MsgID, Job
from ..cp import app
from .. import db

class State(rx.State):
    current_cluster: Cluster = None
    jobs: list[Job] = []

    sort_value = ""
    search_value = ""

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

    @rx.event(background=True)
    async def fetch_cluster(self):
        while True:
            # if self.router.session.client_token not in app.event_namespace.token_to_sid:
            if self.router.page.path != "/clusters/[c_id]":
                print("cluster_overview.py: Stopping background task.")
                break

            async with self:
                self.current_cluster = db.get_cluster(self.cluster_id)
                self.jobs = db.get_all_jobs(self.cluster_id)
            await asyncio.sleep(5)

    @rx.var(cache=True)
    def table_jobs(self) -> list[Job]:
        jobs = self.jobs

        if self.sort_value != "":
            jobs = sorted(
                jobs,
                key=lambda user: getattr(user, self.sort_value).lower(),
            )

        if self.search_value != "":
            jobs = [
                job
                for job in jobs
                if any(
                    self.search_value.lower() in getattr(job, attr).lower()
                    for attr in [
                        "job_id",
                        "email",
                        "group",
                    ]
                )
            ]
        return jobs


def get_job_row(job: Job):
    """Show a job in a table row."""
    return rx.table.row(
        rx.table.cell(
            rx.link(
                job.job_id,
                href=f"/jobs/{job.job_id}",
            )
        ),
        rx.table.cell(job.job_type),
        rx.table.cell(job.created_by),
        rx.table.cell(
            rx.match(
                job.status,
                ("OK", rx.icon("circle-check", color="green")),
                ("WARNING", rx.icon("triangle-alert", color="yellow")),
                rx.text(job.status),
            )
        ),
    )


def jobs_table():
    return rx.vstack(
        rx.hstack(
            rx.select(
                ["job_id", "email", "group"],
                placeholder="Sort By: job_id",
                on_change=State.set_sort_value,
            ),
            rx.input(
                placeholder="Search here...",
                on_change=State.set_search_value,
            ),
        ),
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
                    State.table_jobs,
                    get_job_row,
                )
            ),
            width="100%",
        ),
        rx.text(f"Showing {State.jobs.length()} jobs"),
        width="100%",
    )


def sidebar() -> rx.Component:
    return rx.flex(
        rx.link(rx.text("Overview"), href="/"),
        rx.link(rx.text("SQL Shell"), href="/"),
        #rx.divider(),
        rx.heading("Data", class_name="pb-2 pt-8"),
        rx.link(rx.text("Databases"), href="/"),
        rx.link(rx.text("Backup and Restore"), href="/"),
        rx.link(rx.text("Migrations"), href="/"),
        #rx.divider(),
        rx.heading("Security", class_name="pb-2 pt-8"),
        rx.link(rx.text("SQL Users"), href="/"),
        rx.link(rx.text("Networking"), href="/"),
        #rx.divider(),
        rx.heading("Monitoring", class_name="pb-2 pt-8"),
        rx.link(rx.text("Tools"), href="/"),
        rx.link(rx.text("Metrics"), href="/"),
        rx.link(rx.text("SQL Activity"), href="/"),
        rx.link(rx.text("Insights"), href="/"),
        rx.link(rx.text("Jobs"), href="/"),
        class_name="border-r flex-col min-w-48 p-2",
    )


@rx.page(route="/clusters/[c_id]", on_load=State.fetch_cluster)
@template
def cluster():
    return rx.flex(
        sidebar(),
        rx.flex(
            rx.heading(State.cluster_id),
            rx.flex(
                rx.heading("Name"),
                rx.text(State.current_cluster.cluster_id),
                # rx.heading("Topology"),
                # rx.text(InMemoryTableState.current_cluster.topology),
                rx.heading("Status"),
                rx.text(State.current_cluster.status),
                rx.heading("Created by"),
                rx.text(State.current_cluster.created_by),
                rx.heading("Created at"),
                rx.text(State.current_cluster.created_at),
                rx.heading("Updated by"),
                rx.text(State.current_cluster.updated_by),
                rx.heading("Updated at"),
                rx.text(State.current_cluster.updated_at),
                class_name="align-start flex-col",
            ),
            rx.vstack(
                jobs_table(),
            ),
            class_name="flex-1 flex-col overflow-y-scroll p-2",
        ),
        class_name="flex-1"
    )
