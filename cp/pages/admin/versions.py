# app.py
import asyncio
import json
from typing import Any, Dict, List

import reflex as rx
from pydantic import ValidationError

from ...backend import db
from ...components.main import breadcrumb
from ...cp import app
from ...models import Version
from ...state import AuthState
from ...template import template


# ---- State ----
class State(rx.State):

    versions: List[Version] = []

    # modal visibility
    modal_open: bool = False

    # controls the modal visibility
    notification_dialog_open: bool = False
    notification_dialog_title: str = "Success"
    notification_dialog_msg: str = "All done!"

    def close_success(self):
        self.notification_dialog_open = False

    # draft fields for new region
    version: str = ""

    def open_modal(self):
        # reset draft and open
        self.version = ""

        self.modal_open = True

    def close_modal(self):
        self.modal_open = False

    def remove_version(self, v: Version):
        try:
            db.remove_version(v.version)

            self.notification_dialog_title = "Removed"
            self.notification_dialog_msg = (
                f"Version '{v.version}' was successfully removed"
            )
            self.notification_dialog_open = True

        except Exception as e:
            self.notification_dialog_title = "Error"
            self.notification_dialog_msg = str(e)
            self.notification_dialog_open = True

    def submit_new_version(self):
        """Validate draft with Pydantic, print to stdout, and add to the list."""
        try:
            v = Version(
                version=self.version,
            )
        except ValidationError as ve:
            print("[AddRegion] Validation error:", ve)
            return

        try:
            db.add_version(v)
            self.notification_dialog_title = "Added"
            self.notification_dialog_msg = (
                f"Version '{v.version}' was successfully added"
            )
            self.notification_dialog_open = True

        except Exception as e:
            self.notification_dialog_title = "Error"
            self.notification_dialog_msg = str(e)
            self.notification_dialog_open = True

        self.modal_open = False

    is_running: bool = False

    @rx.event(background=True)
    async def start_bg_event(self):
        if self.is_running:
            return
        async with self:
            self.is_running = True

        while True:
            if (
                self.router.page.path != "/admin/versions"
                or self.router.session.client_token
                not in app.event_namespace.token_to_sid
            ):
                print("/admin/versions: Stopping background task.")
                async with self:
                    self.is_running = False
                break

            async with self:
                self.versions = db.get_versions()
            await asyncio.sleep(5)


# ---- UI bits ----


def notification_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                State.notification_dialog_title, class_name="text-3xl pb-2"
            ),
            rx.dialog.description(
                rx.text(State.notification_dialog_msg, class_name="text-xl pb-8")
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
        open=State.notification_dialog_open,
        on_open_change=State.set_notification_dialog_open,  # keeps state in sync if user closes via overlay/esc
    )


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
                rx.button("Cancel", variant="surface", on_click=State.close_modal),
                rx.button("OK", color_scheme="blue", on_click=State.submit_new_version),
                justify="end",
                spacing="3",
            ),
            max_width="720px",
            padding="20px",
        ),
        open=State.modal_open,
        on_open_change=State.set_modal_open,
    )


@rx.page(
    route="/admin/versions",
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
                rx.button("Add new version", on_click=State.open_modal),
                direction="row-reverse",
                class_name="p-4",
            ),
            rx.flex(main_table(), class_name="flex-1 flex-col overflow-y-scroll p-2"),
            add_version_dialog(),
            notification_dialog(),
            class_name="flex-1 flex-col overflow-hidden",
            on_mount=State.start_bg_event,
        ),
        rx.text("Not Authorized"),
    )
