import reflex as rx

from ..template import template


@rx.page(route="/settings", title="Settings")
@template
def settings():
    return rx.flex(
        rx.button("click"),
        rx.text("Settings", class_name="font-bold border-b text-3xl"),
        class_name="flex-1 flex-col overflow-y-scroll p-2",
    )
