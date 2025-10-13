import reflex as rx

from ..state import AuthState
from .main import user_profile_menu


def navbar():
    return rx.flex(
        rx.text("CockroachDB Control Plane", class_name="text-3xl"),
        rx.spacer(),
        rx.box(
            rx.flex(
                rx.icon("search"),
                rx.text("Search..."),
                class_name="border rounded-3xl p-2 w-96",
            )
        ),
        rx.spacer(),
        rx.color_mode.button(class_name="mx-2"),
        rx.text(AuthState.webuser.username, class_name="font-semibold text-xl mx-2"),
        user_profile_menu(),
        class_name="font-bold p-4 align-center ",
    )
