# app.py
import asyncio
import datetime as dt
import gzip
from typing import List

import reflex as rx
from pydantic import ValidationError
from reflex_monaco import monaco

from ...backend import db
from ...components.main import breadcrumb
from ...components.notify import NotifyState
from ...cp import app
from ...models import STRFTIME, EventType, Playbook, PlaybookOverview, Version
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
        self.playbook_name = value
        self.default_version = ""

        try:
            po: list[PlaybookOverview] = db.get_playbook_versions(self.playbook_name)
        except Exception as e:
            return NotifyState.show("Error", str(e))

        self.playbook_versions = sorted([x.version.strftime(STRFTIME) for x in po])

        # find the default version
        _running_v = ""
        for p in po:
            if p.default_version and p.default_version.strftime(STRFTIME) > _running_v:
                _running_v = p.default_version.strftime(STRFTIME)
                self.playbook_version = p.version.strftime(STRFTIME)

            self.default_version = self.playbook_version

        try:
            p: Playbook = db.get_playbook(self.playbook_name, self.playbook_version)
        except Exception as e:
            return NotifyState.show("Error", str(e))

        self.original_content = gzip.decompress(p.playbook).decode("utf-8")
        self.modified_content = self.original_content

    @rx.event
    def on_version_change(self, v: str):
        self.playbook_version = v

        try:
            p: Playbook = db.get_playbook(self.playbook_name, v)
        except Exception as e:
            return NotifyState.show("Error", str(e))

        self.original_content = gzip.decompress(p.playbook).decode("utf-8")
        self.modified_content = self.original_content

    @rx.event
    def set_default(self):

        self.default_version = self.playbook_version

        try:
            db.set_default_playbook(
                self.playbook_name,
                self.playbook_version,
                self.webuser.username,
            )
            db.insert_event_log(
                self.webuser.username,
                EventType.PLAYBOOK_SET_DEFAULT,
                {"name": self.playbook_name, "version": self.playbook_version},
            )
        except Exception as e:
            return NotifyState.show("Error", str(e))

        return rx.toast.success(
            f"Successfully set version '{self.playbook_version}' as the default version."
        )

    @rx.event
    def delete_version(self):

        if self.playbook_version == self.default_version:
            return rx.toast.error("Cannot delete the default version")

        try:
            db.remove_playbook(
                self.playbook_name,
                self.playbook_version,
            )
            db.insert_event_log(
                self.webuser.username,
                EventType.PLAYBOOK_REMOVE,
                {"name": self.playbook_name, "version": self.playbook_version},
            )
            po: list[PlaybookOverview] = db.get_playbook_versions(self.playbook_name)

        except Exception as e:
            return NotifyState.show("Error", str(e))

        # refresh the list, then move to the default version
        self.playbook_versions = sorted([x.version.strftime(STRFTIME) for x in po])
        self.playbook_version = self.default_version
        self.on_version_change(self.playbook_version)

        return rx.toast.success(
            f"Successfully deleted version '{self.playbook_version}'."
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
        """Update the active view."""

        try:
            p = db.add_playbook(
                self.playbook_name,
                gzip.compress(self.modified_content.encode("utf-8")),
                self.webuser.username,
            )
            db.insert_event_log(
                self.webuser.username,
                EventType.PLAYBOOK_ADD,
                {"name": self.playbook_name, "version": p.version.strftime(STRFTIME)},
            )
            po: list[PlaybookOverview] = db.get_playbook_versions(self.playbook_name)

        except Exception as e:
            return NotifyState.show("Error", str(e))

        # refresh the list, then update the version name of current selected playbook
        self.playbook_versions = sorted([x.version.strftime(STRFTIME) for x in po])
        self.playbook_version = p.version.strftime(STRFTIME)

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
