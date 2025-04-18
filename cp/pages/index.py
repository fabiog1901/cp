import reflex as rx

from ..template import template


@rx.page(route="/", title="Home")
@template
def index():
    return rx.flex(
        rx.heading("HOME SWEET HOME!"),
        # rx.hstack(
        #     new_cluster_dialog(),
        #     direction="row-reverse",
        # ),
        # clusters_table(),
        class_name="flex-1 flex-col overflow-y-scroll p-2",
    )
