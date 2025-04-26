import asyncio

import reflex as rx

from .. import db
from ..models import Job
from ..template import template


class State(rx.State):
    jobs: list[Job] = []

    bg_task: bool = False

    @rx.event(background=True)
    async def fetch_all_jobs(self):
        if self.bg_task:
            return
        async with self:
            self.bg_task = True

        while True:
            # if self.router.session.client_token not in app.event_namespace.token_to_sid:
            if self.router.page.path != "/jobs":
                print("jobs.py: Stopping background task.")
                async with self:
                    self.bg_task = False
                break

            async with self:
                self.jobs = db.get_all_jobs()
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
        rx.table.cell(
            rx.match(
                job.status,
                (
                    "RUNNING",
                    rx.badge(
                        "RUNNING...",
                        class_name="rounded animate-pulse bg-orange-600 text-white px-4 text-xl font-semibold",
                    ),
                ),
                (
                    "COMPLETED",
                    rx.badge(
                        "COMPLETED",
                        class_name="rounded bg-green-600 text-white px-4 text-xl font-semibold",
                    ),
                ),
                (
                    "FAILED",
                    rx.badge(
                        "FAILED",
                        class_name="rounded bg-red-600 text-white px-4 text-xl font-semibold",
                    ),
                ),
                (
                    "PENDING",
                    rx.badge(
                        "PENDING...",
                        class_name="rounded bg-purple-600 text-white px-4 text-xl font-semibold",
                    ),
                ),
                (
                    "ABORTED",
                    rx.badge(
                        "ABORTED",
                        class_name="rounded bg-gray-600 text-white px-4 text-xl font-semibold",
                    ),
                ),
                rx.text(job.status),
            ),
        ),
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


@rx.page(route="/jobs", title="Jobs", on_load=State.fetch_all_jobs)
@template
def jobs():
    return rx.flex(
        rx.text(
            "Jobs",
            class_name="p-2 text-8xl font-semibold",
        ),
        rx.vstack(
            jobs_table(),
            class_name="pt-8",
        ),
        class_name="flex-1 flex-col overflow-y-scroll p-2",
    )
