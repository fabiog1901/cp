import asyncio

import reflex as rx

from .. import db
from ..cp import app
from ..models import Job, MsgID, Task
from ..template import template


class State(rx.State):
    current_job: Job = None
    tasks: list[Task] = []

    sort_value = ""
    search_value = ""

    @rx.var
    def job_id(self) -> str | None:
        return self.router.page.params.get("j_id") or None

    bg_task: bool  = False
    
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

    @rx.var(cache=True)
    def table_tasks(self) -> list[Task]:
        tasks = self.tasks

        if self.sort_value != "":
            tasks = sorted(
                tasks,
                key=lambda user: getattr(user, self.sort_value).lower(),
            )

        if self.search_value != "":
            tasks = [
                job
                for job in tasks
                if any(
                    self.search_value.lower() in getattr(job, attr).lower()
                    for attr in [
                        "job_id",
                        "email",
                        "group",
                    ]
                )
            ]
        return tasks

    



def get_task_row(task: Task):
    """Show a job in a table row."""
    return rx.table.row(
        rx.table.cell(task.created_at),
        rx.table.cell(task.task_name),
        rx.table.cell(task.task_desc),
    )


def tasks_table():
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
                    rx.table.column_header_cell("Created At"),
                    rx.table.column_header_cell("Task Name"),
                    rx.table.column_header_cell("Description"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.table_tasks,
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
        rx.heading(State.job_id),
        rx.flex(
            rx.heading("Name"),
            rx.text(State.current_job.job_id),
            # rx.heading("Topology"),
            # rx.text(InMemoryTableState.current_job.topology),
            rx.heading("Status"),
            rx.text(State.current_job.status),
            rx.heading("Created by"),
            rx.text(State.current_job.created_by),
            rx.heading("Created at"),
            rx.text(State.current_job.created_at),
            class_name="align-start flex-col",
        ),
        rx.vstack(
            tasks_table(),
        ),
        class_name="flex-1 flex-col overflow-y-scroll p-2",
    )
