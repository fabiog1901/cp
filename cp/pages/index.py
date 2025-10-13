import reflex as rx

from ..template import template


@rx.page(route="/", title="Home", on_load=rx.redirect("/clusters"))
@template
def webpage():
    return rx.flex(
        class_name="flex-1 flex-col overflow-y-scroll p-2",
    )
