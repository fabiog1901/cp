import asyncio

import psycopg
import reflex as rx
from psycopg.rows import class_row

from ...backend import db
from ...components.main import cluster_banner, mini_breadcrumb
from ...cp import app
from ...models import BackupDetails, Cluster, JobType, RestoreRequest, StrID
from ...state import AuthState
from ...template import template


class State(AuthState):
    current_cluster: Cluster = None

    paths: list[str] = []
    selected_path: str = ""
    object_type: str = "DATABASE"

    full_cluster: bool = False

    @rx.event
    def set_full_cluster(self, value: bool):
        self.full_cluster = value

    backup_details: list[BackupDetails] = []

    select_value: str = "LATEST"

    @rx.event
    def change_value(self, value: str):
        self.select_value = value

    @rx.event
    def change_object_type(self, value: str):
        self.object_type = value

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

    is_running: bool = False

    @rx.event
    def get_backups(self):
        try:
            with psycopg.connect(
                f"postgres://cockroach:cockroach@{self.current_cluster.lbs_inventory[0].dns_address}:26257/defaultdb?sslmode=require",
                autocommit=True,
                connect_timeout=2,
            ) as conn:
                with conn.cursor() as cur:
                    rs = cur.execute("SHOW BACKUPS IN 'external://backup';").fetchall()

                p = [r[0] for r in rs]
                p.sort(reverse=True)
                self.paths = ["LATEST"] + p

        except Exception as e:
            print(e)
            self.paths = []

    @rx.event
    def get_backup(self, backup_path: str):
        self.selected_path = backup_path
        try:
            with psycopg.connect(
                f"postgres://cockroach:cockroach@{self.current_cluster.lbs_inventory[0].dns_address}:26257/defaultdb?sslmode=require",
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

        except Exception as e:
            print(e)

    @rx.event
    def initiate_restore(self, form_data: dict):
        rr = RestoreRequest(
            name=self.current_cluster.cluster_id,
            backup_path=form_data.get("path"),
            restore_aost=form_data.get("aost"),
            restore_full_cluster=self.full_cluster,
            object_type=self.object_type if not self.full_cluster else None,
            object_name=form_data.get("object_name") if not self.full_cluster else None,
            backup_into=form_data.get("backup_into") if not self.full_cluster else None,
        )
        msg_id: StrID = db.insert_into_mq(
            JobType.RESTORE_CLUSTER,
            rr.model_dump(),
            self.webuser.username,
        )
        db.insert_event_log(
            self.webuser.username,
            JobType.RESTORE_CLUSTER,
            rr.model_dump() | {"job_id": msg_id.id},
        )

        return rx.toast.info(f"Job {msg_id.id} requested.")

    @rx.event(background=True)
    async def start_bg_event(self):
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
                    self.paths = []
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
                self.get_backups()

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
        rx.text(f"Showing {State.paths.length()} backups"),
        width="100%",
    )


def restore_dialog():
    return rx.cond(
        AuthState.is_admin_or_rw,
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
                        rx.text(
                            "Restore Path",
                            class_name="p-2",
                        ),
                        rx.select(
                            State.paths,
                            value=State.select_value,
                            on_change=State.change_value,
                            name="path",
                            required=True,
                            class_name="p-2",
                        ),
                        rx.text(
                            "As of system time",
                            class_name="p-2",
                        ),
                        rx.input(
                            type="datetime-local",
                            name="aost",
                            # default_value=State.selected_name,
                            # on_mount=State.load_funny_name,
                            color_scheme="mint",
                            class_name="p-2",
                        ),
                        rx.box(class_name="p-2"),
                        rx.checkbox(
                            "Restore Full Cluster",
                            on_change=State.set_full_cluster,
                            class_name="",
                        ),
                        rx.box(class_name="p-2"),
                        rx.cond(
                            State.full_cluster,
                            rx.box(),
                            rx.flex(
                                rx.select(
                                    ["DATABASE", "TABLE"],
                                    value=State.object_type,
                                    on_change=State.change_object_type,
                                    name="object_type",
                                    required=True,
                                    class_name="p-2",
                                ),
                                rx.text("Database/Table name", class_name="p-2"),
                                rx.input(
                                    name="object_name",
                                    color_scheme="mint",
                                    class_name="p-2",
                                ),
                                rx.text("Into DB", class_name="p-2"),
                                rx.input(
                                    name="backup_into",
                                    color_scheme="mint",
                                    class_name="p-2",
                                ),
                                class_name="flex flex-1 flex-col",
                            ),
                        ),
                        class_name="flex-col py-2",
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
                rx.text("Restore"),
                disabled=True,
                class_name="cursor-pointer",
            ),
            content="You need to have admin or rw role to create new clusters",
        ),
    )


@rx.page(
    route="/clusters/[c_id]/backups",
    title=f"Cluster {State.current_cluster.cluster_id}: Backups",
    on_load=AuthState.check_login,
)
@template
def webpage():
    return rx.flex(
        cluster_banner(
            "boxes",
            State.current_cluster.cluster_id,
            State.current_cluster.status,
            State.current_cluster.version,
        ),
        rx.hstack(
            restore_dialog(),
            direction="row-reverse",
            class_name="p-4",
        ),
        mini_breadcrumb(State.cluster_id, f"/clusters/{State.cluster_id}", "Backups"),
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
                rx.heading(State.selected_path, class_name="p-2"),
                backup_details_table(),
                class_name="flex-1 flex-col overflow-y-scroll",
            ),
            class_name="flex overflow-hidden pt-8",
        ),
        class_name="flex-col flex-1 overflow-hidden",
        on_mount=State.start_bg_event,
    )
