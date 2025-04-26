import asyncio

import reflex as rx

from .. import db
from ..models import Job, Task, TS_FORMAT
from ..template import template


class State(rx.State):
    current_job: Job = None
    tasks: list[Task] = []

    @rx.var
    def job_id(self) -> str | None:
        return self.router.page.params.get("j_id") or None

    bg_task: bool = False

    @rx.event(background=True)
    async def fetch_tasks(self):
        if self.bg_task:
            return
        async with self:
            self.bg_task = True

        while True:
            # if self.router.session.client_token not in app.event_namespace.token_to_sid:
            if self.router.page.path != "/jobs/[j_id]":
                print("job_overview.py: Stopping background task.")
                async with self:
                    self.bg_task = False
                break

            async with self:
                self.current_job = db.get_job(int(self.job_id))
                self.tasks = db.get_all_tasks(self.job_id)
            await asyncio.sleep(5)


def get_task_row(task: Task):
    """Show a job in a table row."""
    return rx.table.row(
        rx.table.cell(rx.moment(task.created_at, format=TS_FORMAT)),
        rx.table.cell(task.task_name),
        rx.table.cell(task.task_desc),
    )


def tasks_table():
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Created At"),
                    rx.table.column_header_cell("Task"),
                    rx.table.column_header_cell("Description"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.tasks,
                    get_task_row,
                )
            ),
            width="100%",
        ),
        rx.text(f"Showing {State.tasks.length()} jobs"),
        width="100%",
    )


@rx.page(route="/jobs/[j_id]", on_load=State.fetch_tasks)
@template
def job():
    return rx.flex(
        rx.flex(
            rx.hstack(
                rx.text(
                    f"Job {State.current_job.job_id}",
                    class_name="p-2 text-8xl font-semibold",
                ),
                rx.divider(orientation="vertical", size="4", class_name="mx-8"),
                rx.match(
                    State.current_job.status,
                    (
                        "COMPLETED",
                        rx.box(
                            rx.text("COMPLETED"),
                            class_name="rounded bg-green-600 text-white p-2 text-xl font-bold",
                        ),
                    ),
                    (
                        "FAILED",
                        rx.box(
                            "FAILED",
                            class_name="rounded bg-red-600 text-white p-2 text-xl font-bold",
                        ),
                    ),
                ),
                rx.vstack(
                    rx.text("Created At"),
                    rx.moment(State.current_job.created_at, format=TS_FORMAT),
                    class_name="mx-16",
                    align="center",
                ),
                rx.vstack(
                    rx.text("Created By"),
                    rx.text(State.current_job.created_by, format=TS_FORMAT),
                    class_name="mx-16",
                    align="center",
                ),
                align="center",
            ),
            class_name="align-start flex-col",
        ),
        rx.vstack(
            tasks_table(),
            class_name="pt-8",
        ),
        class_name="flex-1 flex-col overflow-y-scroll p-2",
    )
