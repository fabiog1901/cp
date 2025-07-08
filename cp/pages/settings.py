import asyncio

import reflex as rx

from ..state.base import BaseState
from ..template import template

# Define the keys and default values for each section
SECTIONS = {
    "sso": {
        "SSO_REDIRECT_URL": "http://localhost:8080/auth/callback",
        "SSO_CLIENT_ID": "example-client-id",
    },
    "playbook": {
        "DEFAULT_REGION": "us-west-2",
        "RETRY_COUNT": "3",
    },
    "various": {
        "DEBUG_MODE": "true",
        "MAX_CONNECTIONS": "100",
    },
}


class ConfigEditorState(rx.State):
    values: dict[str, str] = {
        key: value for section in SECTIONS.values() for key, value in section.items()
    }

    def update_value(self, key: str, value: str):
        self.values[key] = value


def section_ui(title: str, items: dict[str, str]) -> rx.Component:
    return rx.vstack(
        rx.heading(title.capitalize(), size="4", margin_bottom="1rem"),
        *[
            rx.hstack(
                rx.text(key, width="200px"),
                rx.input(
                    value=ConfigEditorState.values.get(key, ""),
                    on_change=ConfigEditorState.update_value(key),
                    width="400px",
                ),
                spacing="4",
            )
            for key in items
        ],
        spacing="3",
        padding="1rem",
        border="1px solid #ccc",
        border_radius="8px",
        margin_bottom="1rem",
        width="100%",
    )


def config_editor_page() -> rx.Component:
    return rx.container(
        rx.vstack(
            *[
                section_ui(section_name, section_data)
                for section_name, section_data in SECTIONS.items()
            ],
            width="800px",
            spacing="4",
        ),
        padding="2rem",
    )


@rx.page(
    route="/settings",
    title="Settings",
    on_load=BaseState.check_login,
)
@template
def settings():
    return rx.cond(
        BaseState.is_admin,
        rx.flex(
            rx.text("Settings", class_name="font-bold border-b text-3xl"),
            config_editor_page(),
            class_name="flex-1 flex-col overflow-y-scroll p-2",
        ),
        rx.text(
            "Not Authorized",
        ),
    )
