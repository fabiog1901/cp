import asyncio

import reflex as rx

from psycopg.rows import class_row

from .. import db
from ..components.BadgeClusterStatus import get_cluster_status_badge
from ..components.BadgeJobStatus import get_job_status_badge
from ..cp import app
from ..models import Cluster, Job, BackupDetails
from ..state.base import BaseState
from ..template import template

import psycopg


class State(BaseState):
    current_cluster: Cluster = None

    paths: list[str] = []
    backup_details: list[BackupDetails] = []
    jobs: list[Job] = []

    value: str = "LATEST"

    @rx.event
    def change_value(self, value: str):
        """Change the select value var."""
        self.value = value

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

    is_running: bool = False

    @rx.event
    def get_backups(self):
        with psycopg.connect(
            # f"postgres://cockroach:cockroach@{self.current_cluster.lbs_inventory[0].dns_address}:26257/defaultdb?sslmode=require",
            f"postgres://cockroach:cockroach@localhost:26257/defaultdb?sslmode=require",
            autocommit=True,
            connect_timeout=2,
        ) as conn:
            with conn.cursor() as cur:
                rs = cur.execute("SHOW BACKUPS IN 'external://backup';").fetchall()

            self.paths = [r[0] for r in rs] + ["LATEST"]

    @rx.event
    def get_backup(self, backup_path: str):
        with psycopg.connect(
            # f"postgres://cockroach:cockroach@{self.current_cluster.lbs_inventory[0].dns_address}:26257/defaultdb?sslmode=require",
            f"postgres://cockroach:cockroach@localhost:26257/defaultdb?sslmode=require",
            autocommit=True,
            connect_timeout=2,
        ) as conn:
            with conn.cursor(row_factory=class_row(BackupDetails)) as cur:
                rs = cur.execute(
                    f"""
                    select database_name, parent_schema_name, object_name, object_type,end_time 
                    from [SHOW BACKUP '{backup_path}' IN 'external://backup']
                    WHERE database_name NOT IN ('system', 'postgres')
                        or object_name NOT IN ('system', 'postgres') AND object_type = 'database'
                         ;
                    """
                ).fetchall()

            self.backup_details = rs

    def initiate_restore(self, form_data):

        print(form_data)

    @rx.event(background=True)
    async def fetch_cluster(self):
        if self.is_running:
            return
        async with self:
            self.is_running = True

        while True:
            if (
                self.router.page.path != "/clusters/[c_id]/backups"
                or self.router.session.client_token
                not in app.event_namespace.token_to_sid
            ):
                print("cluster_backups.py: Stopping background task.")
                async with self:
                    self.is_running = False
                break

            async with self:
                cluster: Cluster = db.get_cluster(
                    self.cluster_id,
                    list(self.webuser.groups),
                    self.is_admin,
                )
                if cluster is None:
                    self.is_running = False
                    # TODO redirect is buggy
                    return rx.redirect("/404", replace=True)

                self.current_cluster = cluster

            await asyncio.sleep(5)


def get_details_row(bd: BackupDetails):
    return rx.table.row(
        rx.table.cell(bd.object_type),
        rx.table.cell(bd.database_name),
        rx.table.cell(bd.parent_schema_name),
        rx.table.cell(bd.object_name),
        rx.table.cell(bd.end_time),
    )


def backup_details_table():
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Type"),
                    rx.table.column_header_cell("Database"),
                    rx.table.column_header_cell("Schema"),
                    rx.table.column_header_cell("Object"),
                    rx.table.column_header_cell("End Time"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.backup_details,
                    get_details_row,
                )
            ),
            width="100%",
            size="3",
        ),
        rx.text(f"Showing {State.jobs.length()} backups"),
        width="100%",
    )


def restore_dialog():
    return rx.cond(
        BaseState.is_admin_or_rw,
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button(
                    "Restore",
                ),
            ),
            rx.dialog.content(
                rx.dialog.title("Restore", class_name="text-4xl pb-4"),
                rx.form(
                    rx.flex(
                        rx.heading("Cluster Name", size="4"),
                        rx.select(
                            State.paths,
                            value=State.value,
                            on_change=State.change_value,
                            name="folderz"
                        ),
                        rx.input(
                            type="date",
                            name="datez",
                            # default_value=State.selected_name,
                            # on_mount=State.load_funny_name,
                            color_scheme="mint",
                            class_name="",
                        ),
                        rx.input(
                            type="time",
                            name="timez",
                            # default_value=State.selected_name,
                            # on_mount=State.load_funny_name,
                            color_scheme="mint",
                            class_name="",
                        ),
                        direction="column",
                        spacing="4",
                    ),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="soft",
                                color_scheme="gray",
                            ),
                        ),
                        rx.dialog.close(
                            rx.button("Submit", type="submit"),
                        ),
                        spacing="3",
                        justify="end",
                    ),
                    on_submit=lambda form_data: State.initiate_restore(form_data),
                    reset_on_submit=False,
                ),
                max_width="850px",
            ),
        ),
        rx.tooltip(
            rx.button(
                rx.icon("plus"),
                rx.text("New Cluster"),
                disabled=True,
                class_name="cursor-pointer",
            ),
            content="You need to have admin or rw role to create new clusters",
        ),
    )


@rx.page(
    route="/clusters/[c_id]/backups",
    on_load=BaseState.check_login,
)
@template
def cluster():
    return rx.flex(
        rx.hstack(
            rx.icon("boxes", size=100, class_name="p-2"),
            rx.text(
                State.current_cluster.cluster_id,
                class_name="p-2 text-8xl font-semibold",
            ),
            rx.divider(orientation="vertical", size="4", class_name="mx-8"),
            get_cluster_status_badge(State.current_cluster.status),
            rx.hstack(
                rx.vstack(
                    rx.text("Version"),
                    rx.text(
                        State.current_cluster.version,
                        class_name="text-3xl font-semibold",
                    ),
                    class_name="mx-16",
                    align="center",
                ),
                direction="row-reverse",
                class_name="p-4 flex-1",
            ),
            align="center",
        ),
        rx.hstack(
            rx.button(
                "Fetch",
                on_click=State.get_backups,
            ),
            restore_dialog(),
            direction="row-reverse",
            class_name="p-4",
        ),
        rx.hstack(
            rx.link(
                rx.text(
                    State.cluster_id,
                    class_name="p-2 pt-2 font-semibold text-2xl",
                ),
                href=f"/clusters/{State.cluster_id}",
            ),
            rx.text(" > ", class_name="p-2 pt-2 font-semibold text-2xl"),
            rx.text("Backups", class_name="p-2 pt-2 font-semibold text-2xl"),
            class_name="p-2",
        ),
        rx.flex(
            rx.flex(
                rx.vstack(
                    rx.foreach(
                        State.paths,
                        lambda x: rx.hstack(
                            rx.button(
                                x,
                                class_name="cursor-pointer",
                                on_click=State.get_backup(x),
                            ),
                        ),
                    ),
                    class_name="px-8",
                ),
                class_name="flex w-80  flex-col overflow-y-scroll",
            ),
            rx.flex(
                backup_details_table(),
                class_name="flex-1 flex-col overflow-y-scroll",
            ),
            class_name="flex overflow-hidden pt-8",
        ),
        class_name="flex-col flex-1 overflow-hidden",
        on_mount=rx.cond(
            BaseState.is_logged_in,
            State.fetch_cluster,
            BaseState.just_return,
        ),
    )
