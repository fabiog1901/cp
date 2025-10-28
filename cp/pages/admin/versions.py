# app.py
import asyncio
from typing import List

import reflex as rx
from pydantic import ValidationError

from ...backend import db
from ...components.main import breadcrumb
from ...components.notify import NotifyState
from ...cp import app
from ...models import EventType, Version
from ...state import AuthState
from ...template import template

ROUTE = "/admin/versions"


class State(AuthState):

    versions: List[Version] = []

    version: str = ""

    # modal visibility
    dialog_open: bool = False

    def open_dialog(self):
        # reset draft and open
        self.version = ""

        self.dialog_open = True

    def close_dialog(self):
        self.dialog_open = False

    def remove_version(self, v: Version):
        try:
            db.remove_version(v.version)

            db.insert_event_log(
                self.webuser.username,
                EventType.VERSION_REMOVE,
                v.version,
            )
        except Exception as e:
            return NotifyState.show("Error", str(e))

    def submit_new_version(self):
        """Validate draft with Pydantic, print to stdout, and add to the list."""

        self.dialog_open = False

        try:
            v = Version(
                version=self.version,
            )

            db.add_version(v)

            db.insert_event_log(
                self.webuser.username,
                EventType.VERSION_ADD,
                v.version,
            )
        except ValidationError as ve:
            return NotifyState.show("Validation Error", str(ve))
        except Exception as e:
            return NotifyState.show("Error", str(e))

    is_running: bool = False

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
                    self.versions = db.get_versions()
                except Exception as e:
                    self.is_running = False
                    return NotifyState.show("Error", str(e))

            await asyncio.sleep(5)


def table_row(v: Version) -> rx.Component:
    return rx.table.row(
        rx.table.cell(v.version),
        rx.table.cell(remove_version_dialog(v)),
    )


def main_table() -> rx.Component:
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Version"),
                    rx.table.column_header_cell(""),
                )
            ),
            rx.table.body(
                rx.foreach(
                    State.versions,
                    table_row,
                )
            ),
            width="100%",
        ),
        rx.text(f"Showing {State.versions.length()} versions"),
        width="100%",
        size="3",
    )


def remove_version_dialog(v: Version) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            rx.box(
                rx.tooltip(
                    rx.icon(
                        "trash-2",
                        color=None,
                        size=30,
                        class_name="cursor-pointer text-red-500 hover:text-red-300",
                    ),
                    content="Remove version",
                ),
            ),
        ),
        rx.alert_dialog.content(
            rx.alert_dialog.title(f"Remove region '{v.version}' ?"),
            rx.alert_dialog.description(
                " ",
                size="4",
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
                        on_click=lambda: State.remove_version(v),
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            style={"max_width": 450},
        ),
    )


def add_version_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Add New Version"),
            rx.dialog.description("Fill in the details for the new version."),
            rx.vstack(
                rx.hstack(
                    rx.input(
                        value=State.version,
                        on_change=State.set_version,
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            rx.hstack(
                rx.button("Cancel", variant="surface", on_click=State.close_dialog),
                rx.button("OK", color_scheme="blue", on_click=State.submit_new_version),
                justify="end",
                spacing="3",
            ),
            max_width="720px",
            padding="20px",
        ),
        open=State.dialog_open,
        on_open_change=State.set_dialog_open,
    )


@rx.page(
    route=ROUTE,
    title="Versions",
    on_load=AuthState.check_login,
)
@template
def webpage() -> rx.Component:
    return rx.cond(
        AuthState.is_admin,
        rx.flex(
            breadcrumb("Admin", "/admin/", "Versions"),
            rx.hstack(
                rx.button("Add new version", on_click=State.open_dialog),
                direction="row-reverse",
                class_name="p-4",
            ),
            rx.flex(main_table(), class_name="flex-1 flex-col overflow-y-scroll p-2"),
            add_version_dialog(),
            class_name="flex-1 flex-col overflow-hidden",
            on_mount=State.start_bg_event,
        ),
        rx.text("Not Authorized"),
    )
