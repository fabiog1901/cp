# app.py
import datetime as dt

import reflex as rx
from reflex_monaco import monaco

from ...components.main import breadcrumb
from ...components.notify import NotifyState
from ...services import playbooks_service
from ...state import AuthState
from ...template import template

ROUTE = "/admin/playbooks"

PLAYBOOK = [
    "CREATE_CLUSTER",
    "DELETE_CLUSTER",
    "HEALTHCHECK_CLUSTER",
    "RESTORE_CLUSTER",
    "SCALE_CLUSTER_IN",
    "SCALE_CLUSTER_OUT",
    "SCALE_DISK_SIZE",
    "SCALE_NODE_CPUS",
    "UPGRADE_CLUSTER",
]


class State(AuthState):

    playbook_name: str = ""
    playbook_version: str = ""
    default_version: str = ""
    created_at: dt.datetime = ""
    created_by: str = ""
    updated_at: dt.datetime = ""

    playbook_versions: list[str] = []

    original_content: str = ""
    modified_content: str = ""

    @rx.event
    def on_playbook_change(self, value: str):
        try:
            selection = playbooks_service.load_playbook_selection(value)
        except Exception as e:
            return NotifyState.show("Error", str(e))

        self.playbook_name = selection["playbook_name"]
        self.playbook_version = selection["playbook_version"]
        self.default_version = selection["default_version"]
        self.playbook_versions = selection["playbook_versions"]
        self.original_content = selection["original_content"]
        self.modified_content = selection["modified_content"]

    @rx.event
    def on_version_change(self, v: str):
        try:
            selection = playbooks_service.load_playbook_version(self.playbook_name, v)
        except Exception as e:
            return NotifyState.show("Error", str(e))

        self.playbook_version = selection["playbook_version"]
        self.original_content = selection["original_content"]
        self.modified_content = selection["modified_content"]

    @rx.event
    def set_default(self):
        try:
            playbooks_service.set_default_playbook(
                self.playbook_name, self.playbook_version, self.webuser.username
            )
        except Exception as e:
            return NotifyState.show("Error", str(e))

        self.default_version = self.playbook_version
        return rx.toast.success(
            f"Successfully set version '{self.playbook_version}' as the default version."
        )

    @rx.event
    def delete_version(self):
        try:
            selection = playbooks_service.delete_playbook_version(
                self.playbook_name,
                self.playbook_version,
                self.default_version,
                self.webuser.username,
            )
        except ValueError as e:
            return rx.toast.error(str(e))
        except Exception as e:
            return NotifyState.show("Error", str(e))

        deleted_version = self.playbook_version
        self.playbook_versions = selection["playbook_versions"]
        self.playbook_version = selection["playbook_version"]
        self.default_version = selection["default_version"]
        self.original_content = selection["original_content"]
        self.modified_content = selection["modified_content"]

        return rx.toast.success(
            f"Successfully deleted version '{deleted_version}'."
        )

    @rx.event
    def revert_changes(self):
        """Load the file content."""
        self.modified_content = self.original_content

    @rx.event
    def on_change(self, value: str):
        """Update the modified content."""
        self.modified_content = value

    @rx.event
    def save_changes(self):
        try:
            selection = playbooks_service.save_playbook_content(
                self.playbook_name,
                self.modified_content,
                self.webuser.username,
            )
        except Exception as e:
            return NotifyState.show("Error", str(e))

        self.playbook_versions = selection["playbook_versions"]
        self.playbook_version = selection["playbook_version"]
        self.original_content = selection["original_content"]
        self.modified_content = selection["modified_content"]

        return rx.toast.success(
            f"Successfully saved new version of {self.playbook_name}"
        )


def remove_version_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(rx.button("Delete Version")),
        rx.alert_dialog.content(
            rx.alert_dialog.title(f"Delete version '{State.default_version}' ?"),
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
                        on_click=lambda: State.delete_version,
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
    route=ROUTE,
    title="Playbooks",
    on_load=AuthState.check_login,
)
@template
def webpage() -> rx.Component:
    return rx.cond(
        AuthState.is_admin,
        rx.flex(
            breadcrumb("Admin", "/admin/", "Playbooks"),
            rx.hstack(
                rx.select(
                    PLAYBOOK,
                    value=State.playbook_name,
                    on_change=State.on_playbook_change,
                    width="20em",
                ),
                rx.select(
                    State.playbook_versions,
                    value=State.playbook_version,
                    on_change=State.on_version_change,
                    width="20em",
                ),
                rx.text("Default version:"),
                rx.badge(State.default_version),
                rx.button("Reset", on_click=State.revert_changes),
                rx.button("Save", on_click=State.save_changes),
                rx.button("Set Default", on_click=State.set_default),
                rx.spacer(),
                remove_version_dialog(),
                padding="1em",
            ),
            monaco(
                default_language="yaml",
                default_value="",
                value=State.modified_content,
                on_change=State.on_change.debounce(1000),
                # height="500px",
                options={"fontSize": 14},
                width="100%",
            ),
            class_name="flex-1 flex-col overflow-hidden",
            # on_mount=State.start_bg_event,
        ),
        rx.text("Not Authorized"),
    )
