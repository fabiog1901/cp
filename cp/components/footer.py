import reflex as rx


def footer():
    return rx.flex(
        rx.text("Footer", class_name="text-xl"),
        class_name="font-bold p-4 align-center ",
    )
