import asyncio

import reflex as rx

from .. import db
from ..cp import app
from ..models import TS_FORMAT, Cluster, Job
from ..template import template
from ..components.BadgeClusterStatus import get_cluster_status_badge
from ..components.BadgeJobStatus import get_job_status_badge
import yaml


class State(rx.State):
    current_cluster: Cluster = None
    current_cluster_description: str = ""
    jobs: list[Job] = []

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

    bg_task: bool = False

    @rx.event(background=True)
    async def fetch_cluster(self):
        if self.bg_task:
            return
        async with self:
            self.bg_task = True

        while True:
            # if self.router.session.client_token not in app.event_namespace.token_to_sid:
            if self.router.page.path != "/clusters/[c_id]":
                print("cluster_overview.py: Stopping background task.")
                async with self:
                    self.bg_task = False
                break

            async with self:

                cluster: Cluster = db.get_cluster(self.cluster_id)
                self.current_cluster_description = yaml.safe_dump(cluster.description)
                self.current_cluster = cluster
                self.jobs = db.get_all_jobs(self.cluster_id)
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


def cluster_sidebar() -> rx.Component:
    return rx.flex(
        rx.link(rx.text("Overview", class_name="py-2"), href="/"),
        rx.link(rx.text("SQL Shell", class_name="py-2"), href="/"),
        # rx.divider(),
        rx.heading("Data", class_name="pb-2 pt-8"),
        rx.link(rx.text("Databases", class_name="py-2"), href="/"),
        rx.link(rx.text("Backup and Restore", class_name="py-2"), href="/"),
        rx.link(rx.text("Migrations", class_name="py-2"), href="/"),
        # rx.divider(),
        rx.heading("Security", class_name="pb-2 pt-8"),
        rx.link(rx.text("SQL Users", class_name="py-2"), href="/"),
        rx.link(rx.text("Networking", class_name="py-2"), href="/"),
        # rx.divider(),
        rx.heading("Monitoring", class_name="pb-2 pt-8"),
        rx.link(rx.text("Tools", class_name="py-2"), href="/"),
        rx.link(rx.text("Metrics", class_name="py-2"), href="/"),
        rx.link(rx.text("SQL Activity", class_name="py-2"), href="/"),
        rx.link(rx.text("Insights", class_name="py-2"), href="/"),
        rx.link(rx.text("Jobs", class_name="py-2"), href="/"),
        class_name="border-r flex-col min-w-48 p-2",
    )


@rx.page(route="/clusters/[c_id]", on_load=State.fetch_cluster)
@template
def cluster():
    return rx.flex(
        rx.hstack(
            rx.icon("boxes", size=100, class_name="p-2"),
            rx.text(
                State.current_cluster.cluster_id,
                class_name="p-2 text-8xl font-semibold",
            ),
            rx.divider(orientation="vertical", size="4", class_name="mx-8"),
            get_cluster_status_badge(State.current_cluster.status),
            rx.vstack(
                rx.text("Created At"),
                rx.moment(State.current_cluster.created_at, format=TS_FORMAT),
                class_name="mx-16",
                align="center",
            ),
            rx.vstack(
                rx.text("Created By"),
                rx.text(State.current_cluster.created_by, format=TS_FORMAT),
                class_name="mx-16",
                align="center",
            ),
            align="center",
        ),
        rx.flex(
            cluster_sidebar(),
            rx.flex(
                rx.code_block(
                    State.current_cluster_description,
                    language="yaml",
                    show_line_numbers=True,
                ),
                rx.flex(
                    jobs_table(),
                    class_name="flex-1 flex-col overflow-y-scroll p-2",
                ),
                class_name="flex-1 flex-col overflow-hidden"
            ),
            class_name="flex-1 pt-8 overflow-hidden",
        ),
        class_name="flex-col flex-1 overflow-hidden",
    )
