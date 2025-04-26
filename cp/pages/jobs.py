import asyncio

import reflex as rx

from .. import db
from ..cp import app
from ..models import Job, MsgID

# from ..state import State
from ..template import template


class State(rx.State):
    current_job: Job = None
    jobs: list[Job] = []

    sort_value = ""
    search_value = ""
    bg_task: bool  = False

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

    @rx.event
    def get_job(self, job_id):
        self.current_job = db.get_job(job_id)


def get_job_row(job: Job):
    """Show a job in a table row."""
    return rx.table.row(
        rx.table.cell(
            rx.link(
                job.job_id,
                on_click=State.get_job(job.job_id),
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


@rx.page(route="/jobs", title="Jobs", on_load=State.fetch_all_jobs)
@template
def jobs():
    return rx.flex(
        rx.hstack(
            direction="row-reverse",
        ),
        jobs_table(),
        class_name="flex-1 flex-col overflow-y-scroll p-2",
    )
