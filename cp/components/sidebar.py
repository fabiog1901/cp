import reflex as rx


def get_link(icon: str, name: str, href: str = None):
    return (
        rx.link(
            rx.hstack(
                rx.icon(icon),
                rx.text(name),
            ),
            href=href if href else name.lower(),
            class_name="m-2",
        ),
    )


def sidebar() -> rx.Component:
    return rx.flex(
        get_link("house", "home", "/"),
        get_link("boxes", "Test"),
        # get_link("layout-dashboard", "Console"),
        rx.spacer(),
        get_link("settings", "Settings"),
        class_name="border-r flex-col min-w-48 p-2",
    )
