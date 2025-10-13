import asyncio

import reflex as rx

from ...backend import db
from ...components.BadgeJobStatus import get_job_status_badge
from ...cp import app
from ...models import Job
from ...state import BaseState
from ...template import template


class State(BaseState):
    jobs: list[Job] = []

    is_running: bool = False

    @rx.event(background=True)
    async def fetch_all_jobs(self):
        if self.is_running:
            return
        async with self:
            self.is_running = True

        while True:
            if (
                self.router.page.path != "/jobs"
                or self.router.session.client_token
                not in app.event_namespace.token_to_sid
            ):
                print("jobs.py: Stopping background task.")
                async with self:
                    self.is_running = False
                break

            async with self:
                self.jobs = db.fetch_all_jobs(list(self.webuser.groups), self.is_admin)
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


@rx.page(route="/jobs", title="Jobs", on_load=BaseState.check_login)
@template
def jobs():
    return rx.flex(
        rx.text(
            "Jobs",
            class_name="p-2 text-8xl font-semibold",
        ),
        rx.vstack(
            jobs_table(),
            class_name="flex-1 flex-col overflow-y-scroll pt-8",
        ),
        class_name="flex-1 flex-col overflow-hidden",
        on_mount=rx.cond(
            BaseState.is_logged_in,
            State.fetch_all_jobs,
            BaseState.just_return,
        ),
    )
