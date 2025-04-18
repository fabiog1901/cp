import reflex as rx


def get_link(icon: str, name: str, href: str = None):
    return (
        rx.link(
            rx.hstack(
                rx.icon(icon),
                rx.text(name),
            ),
            href=href if href else f"/{name.lower()}",
            class_name="m-2",
        ),
    )


def sidebar() -> rx.Component:
    return rx.flex(
        get_link("house", "Home", "/"),
        get_link("boxes", "Clusters"), 
        get_link("clipboard-list", "Jobs"),
        rx.spacer(),
        get_link("settings", "Settings"),
        class_name="border-r flex-col min-w-48 p-2",
    )
