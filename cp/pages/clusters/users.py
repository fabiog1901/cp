import asyncio

import psycopg
import reflex as rx
from psycopg.rows import class_row

from ...backend import db
from ...components.BadgeClusterStatus import get_cluster_status_badge
from ...cp import app
from ...models import Cluster, DatabaseUser, JobType, NewDatabaseUserRequest, StrID
from ...state import AuthState
from ...template import template


class State(AuthState):
    current_cluster: Cluster = None

    database_users: list[DatabaseUser] = []

    # controls the modal visibility
    dialog_open: bool = False
    # optional message
    dialog_title: str = "Success"
    dialog_msg: str = "All done!"

    def close_success(self):
        self.dialog_open = False

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

    is_running: bool = False

    @rx.event
    def get_users(self):
        try:
            with psycopg.connect(
                f"postgres://cockroach:cockroach@{self.current_cluster.lbs_inventory[0].dns_address}:26257/defaultdb?sslmode=require",
                autocommit=True,
                connect_timeout=2,
            ) as conn:
                with conn.cursor(row_factory=class_row(DatabaseUser)) as cur:
                    self.database_users = cur.execute(
                        "select username, options, member_of from [show users] where username not in ('admin', 'root', 'cockroach');"
                    ).fetchall()

        except Exception as e:
            print(e)

    @rx.event
    def add_new_user(self, form_data):
        try:
            with psycopg.connect(
                f"postgres://cockroach:cockroach@{self.current_cluster.lbs_inventory[0].dns_address}:26257/defaultdb?sslmode=require",
                autocommit=True,
                connect_timeout=2,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"CREATE USER {form_data.get('username')} WITH password '{form_data.get('password')}'"
                    )

            self.dialog_title = "Success"
            self.dialog_msg = f"User '{form_data.get('username')}' created"
            self.dialog_open = True

        except Exception as e:
            self.dialog_title = "Error"
            self.dialog_msg = str(e)
            self.dialog_open = True

    @rx.event
    def remove_user(self, x: DatabaseUser):
        try:
            with psycopg.connect(
                f"postgres://cockroach:cockroach@{self.current_cluster.lbs_inventory[0].dns_address}:26257/defaultdb?sslmode=require",
                autocommit=True,
                connect_timeout=2,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"DROP USER {x.username}")

            self.dialog_title = "Success"
            self.dialog_msg = f"User '{x.username}' removed successfully"
            self.dialog_open = True

        except Exception as e:
            self.dialog_title = "Error"
            self.dialog_msg = str(e)
            self.dialog_open = True

    # TODO protect from sql injections
    @rx.event
    def remove_user_role(self, username: str, role: str):
        try:
            with psycopg.connect(
                f"postgres://cockroach:cockroach@{self.current_cluster.lbs_inventory[0].dns_address}:26257/defaultdb?sslmode=require",
                autocommit=True,
                connect_timeout=2,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"REVOKE {role} FROM  {username}")

        except Exception as e:

            print(e)

    @rx.event
    def edit_user(self, form_data: dict):
        username = form_data.get("username")
        password = form_data.get("password")

        try:
            with psycopg.connect(
                f"postgres://cockroach:cockroach@{self.current_cluster.lbs_inventory[0].dns_address}:26257/defaultdb?sslmode=require",
                autocommit=True,
                connect_timeout=2,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"ALTER USER {username} WITH password '{password}'")

        except Exception as e:
            print(e)

    @rx.event(background=True)
    async def start_bg_event(self):
        if self.is_running:
            return
        async with self:
            self.is_running = True

        while True:
            if (
                self.router.page.path != "/clusters/[c_id]/users"
                or self.router.session.client_token
                not in app.event_namespace.token_to_sid
            ):
                print("cluster_users.py: Stopping background task.")
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
                self.get_users()

            await asyncio.sleep(5)


def get_table_row(x: DatabaseUser):
    return rx.table.row(
        rx.table.cell(x.username),
        rx.table.cell(x.options),
        rx.table.cell(
            rx.foreach(
                x.member_of,
                lambda membership: rx.hstack(
                    rx.flex(
                        rx.text(membership),
                        remove_user_role_dialog(x.username, membership),
                        class_name="flex border rounded-3xl p-2 px-4 mb-1",
                    ),
                ),
            ),
        ),
        rx.table.cell(
            rx.hstack(
                edit_user_dialog(x.username),
                remove_user_dialog(x),
            ),
        ),
    )


def database_users_table():
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Username"),
                    rx.table.column_header_cell("Options"),
                    rx.table.column_header_cell("Member of"),
                    rx.table.column_header_cell(""),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.database_users,
                    get_table_row,
                )
            ),
            width="100%",
            size="3",
        ),
        rx.text(f"Showing {State.database_users.length()} users"),
        width="100%",
    )


def new_user_dialog():
    return rx.cond(
        AuthState.is_admin_or_rw,
        rx.dialog.root(
            rx.dialog.trigger(
                rx.button(
                    "New User",
                ),
            ),
            rx.dialog.content(
                rx.dialog.title("New User", class_name="text-4xl pb-4"),
                rx.form.root(
                    rx.flex(
                        rx.text(
                            "Username",
                            class_name="p-2",
                        ),
                        rx.box(class_name="p-2"),
                        rx.input(
                            name="username",
                            color_scheme="mint",
                            class_name="p-2",
                        ),
                        rx.box(class_name="p-2"),
                        rx.text(
                            "Password",
                            class_name="p-2",
                        ),
                        rx.input(
                            type="password",
                            name="password",
                            minlength="4",
                            required=True,  # TODO doesn't work...
                            color_scheme="mint",
                            class_name="p-2",
                        ),
                        rx.box(class_name="p-2"),
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
                            rx.button("Add", type="submit"),
                        ),
                        spacing="3",
                        justify="end",
                    ),
                    on_submit=lambda form_data: State.add_new_user(form_data),
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


def edit_user_dialog(user: str):
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.icon(
                "user-pen",
                class_name="text-gray-700 hover:text-gray-400 cursor-pointer",
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(f"Edit User {user}", class_name="text-4xl pb-4"),
            rx.form(
                rx.flex(
                    rx.text(
                        "New Password",
                        class_name="p-2",
                    ),
                    rx.input(
                        type="password",
                        name="password",
                        color_scheme="mint",
                        class_name="p-2",
                    ),
                    rx.box(class_name="p-2"),
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
                on_submit=lambda form_data: State.edit_user(form_data),
                reset_on_submit=False,
            ),
            max_width="850px",
        ),
    )


def remove_user_dialog(x: DatabaseUser):
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            rx.box(
                rx.tooltip(
                    rx.icon(
                        "x",
                        color=None,
                        size=30,
                        class_name="cursor-pointer text-red-500 hover:text-red-300",
                    ),
                    content="Remove user",
                ),
            ),
        ),
        rx.alert_dialog.content(
            rx.alert_dialog.title(f"Remove {x.username}?"),
            rx.alert_dialog.description(
                size="2",
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Remove",
                        color_scheme="red",
                        variant="solid",
                        on_click=lambda: State.remove_user(
                            x,
                        ),
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            style={"max_width": 450},
        ),
    )


def remove_user_role_dialog(user: str, membership: str):
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            rx.box(
                rx.tooltip(
                    rx.icon(
                        "x",
                        color=None,
                        class_name="cursor-pointer text-red-500 hover:text-red-300",
                    ),
                    content="Remove membership",
                ),
            ),
        ),
        rx.alert_dialog.content(
            rx.alert_dialog.title(f"Revoke {membership} from {user}?"),
            rx.alert_dialog.description(
                size="2",
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Revoke",
                        color_scheme="red",
                        variant="solid",
                        on_click=lambda: State.remove_user_role(user, membership),
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            style={"max_width": 450},
        ),
    )


@rx.page(
    route="/clusters/[c_id]/users",
    on_load=AuthState.check_login,
)
@template
def webpage():
    return rx.flex(
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title(State.dialog_title, class_name="text-3xl pb-2"),
                rx.dialog.description(
                    rx.text(State.dialog_msg, class_name="text-xl pb-8")
                ),
                rx.hstack(
                    rx.button("OK", on_click=State.close_success),
                    justify="end",
                    spacing="3",
                ),
                # a bit of styling
                max_width="420px",
                padding="20px",
            ),
            open=State.dialog_open,
            on_open_change=State.set_dialog_open,  # keeps state in sync if user closes via overlay/esc
        ),
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
            new_user_dialog(),
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
            rx.text("Users", class_name="p-2 pt-2 font-semibold text-2xl"),
            class_name="p-2",
        ),
        rx.flex(
            rx.flex(
                rx.heading("Users", class_name="p-2"),
                database_users_table(),
                class_name="flex-1 flex-col overflow-y-scroll",
            ),
            class_name="flex overflow-hidden pt-8",
        ),
        class_name="flex-col flex-1 overflow-hidden",
        on_mount=State.start_bg_event,
    )
