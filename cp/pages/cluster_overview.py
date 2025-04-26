import asyncio

import reflex as rx

from .. import db
from ..cp import app
from ..models import Cluster, Job
from ..template import template


class State(rx.State):
    current_cluster: Cluster = None
    jobs: list[Job] = []

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None
    
    bg_task: bool  = False


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
                self.current_cluster = db.get_cluster(self.cluster_id)
                self.jobs = db.get_all_jobs(self.cluster_id)
            await asyncio.sleep(5)


def get_job_row(job: Job):
    """Show a job in a table row."""
    return rx.table.row(
        rx.table.cell(
            rx.link(
                rx.heading(job.job_id, size="2"),
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
        rx.box(class_name="p-4"),
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
        ),
        rx.text(f"Showing {State.jobs.length()} jobs"),
        width="100%",
    )


def sidebar() -> rx.Component:
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
            rx.icon("boxes", size=48),
            rx.heading(State.current_cluster.cluster_id, size="8"),
            class_name="p-2",
        ),
        rx.divider(size="4"),
        rx.flex(
            sidebar(),
            rx.flex(
                rx.flex(
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
                # rx.flex(
                #     jobs_table(),
                #     class_name="flex-1 flex-col overflow-y-scroll p-2",
                # ),
                class_name="flex-1 flex-col overflow-y-hidden p-2",
            ),
            class_name="flex-1 overflow-hidden",
        ),
        class_name="flex-col flex-1 overflow-hidden",
    )
