import asyncio

import reflex as rx
import yaml

from ...backend import db
from ...components.BadgeJobStatus import get_job_status_badge
from ...components.notify import NotifyState
from ...cp import app
from ...models import TS_FORMAT, Job, JobType, StrID, Task
from ...state import AuthState
from ...template import template

ROUTE = "/jobs/[j_id]"


class State(AuthState):
    current_job: Job = None
    current_job_description: str = ""
    linked_clusters: list[StrID] = []
    tasks: list[Task] = []

    @rx.var
    def job_id(self) -> str | None:
        return self.router.page.params.get("j_id") or None

    is_running: bool = False

    @rx.event
    def reschedule_job(self):
        # TODO fix so we can use self.current_job.descripton

        try:
            j: Job = db.fetch_job(
                self.current_job.job_id, list(self.webuser.groups), self.is_admin
            )
        except Exception as e:
            return NotifyState.show("Error", str(e))

        job_type = (
            JobType.RECREATE_CLUSTER
            if self.current_job.job_type == JobType.CREATE_CLUSTER
            else self.current_job.job_type
        )

        try:
            msg_id: StrID = db.insert_into_mq(
                job_type, j.description, self.webuser.username
            )

            db.insert_event_log(
                self.webuser.username, job_type, j.description | {"job_id": msg_id.id}
            )
        except Exception as e:
            return NotifyState.show("Error", str(e))

        return rx.toast.info(f"Job {msg_id.id} requested.")

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
                    job: Job = db.fetch_job(
                        int(self.job_id), list(self.webuser.groups), self.is_admin
                    )
                except Exception as e:
                    self.is_running = False
                    return NotifyState.show("Error", str(e))

                if job is None:
                    self.is_running = False
                    return rx.redirect("/_notfound", replace=True)

                self.current_job_description = yaml.dump(job.description)
                self.current_job = job

                try:
                    self.tasks = db.get_all_tasks(self.job_id)
                    self.linked_clusters = db.get_linked_clusters_from_job(self.job_id)
                except Exception as e:
                    self.is_running = False
                    return NotifyState.show("Error", str(e))

            await asyncio.sleep(5)


def table_row(task: Task):
    """Show a job in a table row."""
    return rx.table.row(
        rx.table.cell(task.task_id),
        rx.table.cell(rx.moment(task.created_at, format=TS_FORMAT, tz="UTC")),
        rx.table.cell(task.task_name),
        rx.table.cell(task.task_desc),
    )


def data_table():
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Task ID"),
                    rx.table.column_header_cell("Created At"),
                    rx.table.column_header_cell("Task"),
                    rx.table.column_header_cell("Description"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.tasks,
                    table_row,
                )
            ),
            width="100%",
        ),
        rx.text(f"Showing {State.tasks.length()} jobs"),
        width="100%",
    )


@rx.page(
    route=ROUTE,
    title=f"Job {State.current_job.job_id}",
    on_load=AuthState.check_login,
)
@template
def webpage():
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
                rx.cond(
                    AuthState.is_admin_or_rw,
                    rx.button(
                        "Restart Job",
                        on_click=lambda: State.reschedule_job,
                        class_name="cursor-pointer text-lg font-semibold",
                    ),
                    rx.tooltip(
                        rx.button(
                            "Restart Job",
                            disabled=True,
                            class_name="cursor-pointer text-lg font-semibold",
                        ),
                        content="You need to have admin or rw role to create new clusters",
                    ),
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
                    rx.hstack(
                        rx.text("( about"),
                        rx.moment(State.current_job.created_at, from_now=True),
                        rx.text(")"),
                    ),
                    rx.box(class_name="py-2"),
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
                    rx.hstack(
                        rx.text("( about"),
                        rx.moment(State.current_job.updated_at, from_now=True),
                        rx.text(")"),
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
                            rx.link(lc.id, href=f"/clusters/{lc.id}"),
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
            data_table(),
            class_name="pt-8 overflow-y-scroll",
        ),
        class_name="flex-1 flex-col overflow-hidden p-2",
        on_mount=State.start_bg_event,
    )
