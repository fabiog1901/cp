import reflex as rx

from ..state.base import BaseState


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
        get_link("receipt-text", "Billing"),
        get_link("bell-ring", "Alerts"),
        # rx.heading("Organization", class_name="pt-12 pb-2"),
        # rx.link("Information", class_name="py-1"),
        # rx.link("Access Management", class_name="py-1"),
        # rx.link("Authentication", class_name="py-1"),
        rx.spacer(),
        rx.cond(
            BaseState.is_admin,
            rx.vstack(
                rx.heading("Admin", class_name="pt-12 pb-2"),
                get_link("hourglass", "Events"),
                get_link("monitor-cog", "Admin"),
            ),
            rx.box(),
        ),
        class_name="border-r flex-col min-w-48 p-2",
    )
