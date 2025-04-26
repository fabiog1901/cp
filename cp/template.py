from typing import Callable

import reflex as rx

from .components.footer import footer
from .components.navbar import navbar
from .components.sidebar import sidebar


def template(page: Callable[[], rx.Component]) -> rx.Component:
    return rx.flex(
        navbar(),
        rx.flex(
            sidebar(),
            page(),
            class_name="p-2 flex-1",
        ),
        footer(),
        class_name="flex-col h-screen",
    )
