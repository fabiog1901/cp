import reflex as rx

from ..template import template
from ..state import State
from ..models import Task


def get_task_row(task: Task):
    return rx.table.row(
        rx.table.cell(task.task_id),
        rx.table.cell(task.created_at),
        rx.table.cell(task.progress),
        rx.table.cell(task.event),
    )


@rx.page(route="/job/[j_id]")
@template
def cluster():
    return rx.flex(
        rx.heading(State.job_id),
        rx.flex(
            rx.heading("JOB"),
            rx.text(State.current_cluster.cluster_id),
            # rx.heading("Topology"),
            # rx.text(InMemoryTableState.current_cluster.topology),
            # rx.heading("Status"),
            # rx.text(State.current_cluster.status),
            # rx.heading("Created by"),
            # rx.text(State.current_cluster.created_by),
            # rx.heading("Created at"),
            # rx.text(State.current_cluster.created_at),
            # rx.heading("Updated by"),
            # rx.text(State.current_cluster.updated_by),
            # rx.heading("Updated at"),
            # rx.text(State.current_cluster.updated_at),
            class_name="align-start flex-col",
        ),
        rx.vstack(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Task ID"),
                        rx.table.column_header_cell("Created At"),
                        rx.table.column_header_cell("Progress"),
                        rx.table.column_header_cell("Event"),
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
            width="100%",
            on_mount=State.load_jobs,
        ),
        class_name="flex-1 flex-col overflow-y-scroll p-2",
    )
