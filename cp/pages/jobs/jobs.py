import asyncio

import reflex as rx

from ...backend import db
from ...components.BadgeJobStatus import get_job_status_badge
from ...components.notify import NotifyState
from ...cp import app
from ...models import Job
from ...state import AuthState
from ...template import template

ROUTE = "/jobs"


class State(AuthState):
    jobs: list[Job] = []

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
                    self.jobs = db.fetch_all_jobs(
                        list(self.webuser.groups), self.is_admin
                    )
                except Exception as e:
                    self.is_running = False
                    return NotifyState.show(
                        "Error communicating with the database", str(e)
                    )

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
    title="Jobs",
    on_load=AuthState.check_login,
)
@template
def webpage():
    return rx.flex(
        rx.text(
            "Jobs",
            class_name="p-2 text-8xl font-semibold",
        ),
        rx.vstack(
            data_table(),
            class_name="flex-1 flex-col overflow-y-scroll pt-8",
        ),
        class_name="flex-1 flex-col overflow-hidden",
        on_mount=State.start_bg_event,
    )
