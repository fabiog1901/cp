import reflex as rx

from ...state import AuthState
from ...template import template


# ---- Reusable "card" link for the admin tiles ----
def admin_tile(title: str, desc: str, href: str) -> rx.Component:
    return rx.link(
        rx.box(
            rx.vstack(
                rx.heading(title, size="4"),
                rx.text(desc, size="2", color="gray"),
                spacing="2",
                align="start",
            ),
            width="100%",
            padding="16px",
            border="1px solid var(--gray-6)",
            border_radius="12px",
            _hover={
                "border": "1px solid var(--accent-8)",
                "box_shadow": "0 4px 14px rgba(0,0,0,0.08)",
            },
            transition="all 0.15s ease",
        ),
        href=href,
        underline="none",
    )


# ---- /admin (index) ----
def admin_index() -> rx.Component:
    return rx.flex(
        rx.text(
            "Admin",
            class_name="p-2 text-8xl font-semibold",
        ),
        rx.vstack(
            rx.text("Choose a section to manage.", color="gray"),
            class_name="p-4",
        ),
        rx.grid(
            admin_tile(
                "Versions",
                "Manage supported software versions.",
                "/admin/versions",
            ),
            admin_tile("Regions", "Add / remove regions and quotas.", "/admin/regions"),
            admin_tile(
                "Group Role Mapping",
                "Manage IdP groups and how they map to CP Roles",
                "/admin/roles",
            ),
            admin_tile("Activity", "Audit logs and recent actions.", "/admin/activity"),
            admin_tile(
                "Settings",
                "Global configurations.",
                "/admin/settings",
            ),
            columns="3",  # responsive: 1col (mobile), 2col (tablet), 3col (desktop)
            gap="16px",
            width="100%",
        ),
        class_name="flex-1 flex-col overflow-hidden",
    )


@rx.page(
    route="/admin",
    title="Admin",
    on_load=AuthState.check_login,
)
@template
def webpage():
    return rx.cond(
        AuthState.is_admin,
        rx.flex(
            admin_index(),
            class_name="flex-1 flex-col overflow-hidden",
        ),
        rx.text(
            "Not Authorized",
        ),
    )
