import reflex as rx

from ..template import template
from ..state import State
from ..models import Job


def get_job_row(job: Job):
    """Show a cluster in a table row."""
    return rx.table.row(
        rx.table.cell(job.job_id),
        rx.table.cell(job.created_by),
        rx.table.cell(
            job.status
            # rx.match(
            #     job.status,
            #     ("OK", rx.icon("circle-check", color="green")),
            #     ("WARNING", rx.icon("triangle-alert", color="yellow")),
            #     rx.icon("circle-help"),
            # )
        ),
    )


@rx.page(route="/cluster/[c_id]")
@template
def cluster():
    return rx.flex(
        rx.heading(State.cluster_id),
        rx.flex(
            rx.heading("Name"),
            rx.text(State.current_cluster.cluster_id),
            # rx.heading("Topology"),
            # rx.text(InMemoryTableState.current_cluster.topology),
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
        rx.vstack(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Name"),
                        rx.table.column_header_cell("Task Name"),
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
            width="100%",
            on_mount=State.load_jobs,
        ),
        class_name="flex-1 flex-col overflow-y-scroll p-2",
    )
