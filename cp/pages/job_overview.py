import asyncio

import reflex as rx
import yaml

from .. import db
from ..components.BadgeJobStatus import get_job_status_badge
from ..models import TS_FORMAT, ClusterID, Job, MsgID, Task
from ..template import template


class State(rx.State):
    current_job: Job = None
    current_job_description: str = ""
    linked_clusters: list[ClusterID] = []
    tasks: list[Task] = []

    @rx.var
    def job_id(self) -> str | None:
        return self.router.page.params.get("j_id") or None

    bg_task: bool = False

    @rx.event
    def reschedule_job(self):
        # TODO fix so we can use self.current_job.descripton
        j: Job = db.get_job(self.current_job.job_id)

        job_type = (
            "RECREATE_CLUSTER"
            if self.current_job.job_type == "CREATE_CLUSTER"
            else self.current_job.job_type
        )

        msg_id: MsgID = db.insert_msg(job_type, j.description, "fab")
        return rx.toast.info(f"Job {msg_id.msg_id} requested.")

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
                job: Job = db.get_job(int(self.job_id))
                self.current_job_description = yaml.dump(job.description)
                self.current_job = job
                self.tasks = db.get_all_tasks(self.job_id)
                self.linked_clusters = db.get_linked_clusters_from_job(self.job_id)
            await asyncio.sleep(5)


def get_task_row(task: Task):
    """Show a job in a table row."""
    return rx.table.row(
        rx.table.cell(rx.moment(task.created_at, format=TS_FORMAT, tz="UTC")),
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
                get_job_status_badge(State.current_job.status),
                rx.spacer(),
                rx.vstack(
                    rx.text("Job Type"),
                    rx.text(
                        State.current_job.job_type, class_name="text-lg font-semibold"
                    ),
                    class_name="mx-16",
                    align="center",
                ),
                rx.button(
                    "Restart Job",
                    on_click=State.reschedule_job,
                    class_name="cursor-pointer text-lg font-semibold",
                ),
                align="center",
            ),
            class_name="align-start flex-col mx-2",
        ),
        rx.flex(
            rx.card(
                rx.text("Description", class_name="text-2xl font-semibold"),
                rx.divider(class_name="my-2"),
                rx.code_block(
                    State.current_job_description,
                    language="yaml",
                    show_line_numbers=True,
                ),
                class_name="min-w-96",
            ),
            rx.card(
                rx.text("Details", class_name="text-2xl font-semibold"),
                rx.divider(class_name="my-2"),
                rx.flex(
                    rx.hstack(
                        rx.text("Created By"),
                        rx.text(
                            State.current_job.created_by,
                            class_name="text-lg font-semibold",
                        ),
                        class_name="py-2",
                        align="center",
                    ),
                    rx.hstack(
                        rx.text("Created At"),
                        rx.text(
                            rx.moment(
                                State.current_job.created_at,
                                format=TS_FORMAT,
                                tz="UTC",
                            ),
                            class_name="text-lg font-semibold",
                        ),
                        class_name="py-2",
                        align="center",
                    ),
                    rx.box(class_name="py-2"),
                    rx.hstack(
                        rx.text("Last Updated By"),
                        rx.text(
                            State.current_job.updated_by,
                            class_name="text-lg font-semibold",
                        ),
                        class_name="py-2",
                        align="center",
                    ),
                    rx.hstack(
                        rx.text("Last Updated At"),
                        rx.text(
                            rx.moment(
                                State.current_job.updated_at,
                                format=TS_FORMAT,
                                tz="UTC",
                            ),
                            class_name="text-lg font-semibold",
                        ),
                        class_name="py-2",
                        align="center",
                    ),
                    class_name="flex-col",
                ),
                class_name="min-w-96 ml-8",
            ),
            rx.card(
                rx.text("Linked To", class_name="text-2xl font-semibold"),
                rx.divider(class_name="my-2"),
                rx.flex(
                    rx.foreach(
                        State.linked_clusters,
                        lambda lc: rx.hstack(
                            rx.link(lc.cluster_id, href=f"/clusters/{lc.cluster_id}"),
                            class_name="py-2",
                            align="center",
                        ),
                    ),
                    class_name="flex-col",
                ),
                class_name="min-w-96 ml-8",
            ),
            class_name="flex-1 p-2 pt-8",
        ),
        rx.vstack(
            tasks_table(),
            class_name="pt-8 overflow-y-scroll",
        ),
        class_name="flex-1 flex-col overflow-hidden p-2",
    )
