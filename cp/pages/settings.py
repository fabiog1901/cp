import asyncio

import reflex as rx

from ..state.base import BaseState
from ..template import template


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
            class_name="flex-1 flex-col overflow-y-scroll p-2",
        ),
        rx.text(
            "Not Authorized",
        ),
    )
