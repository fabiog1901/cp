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
    return rx.vstack(
        rx.heading("Admin", size="7"),
        rx.text("Choose a section to manage.", color="gray"),
        rx.grid(
            admin_tile(
                "Settings",
                "Global configuration, authentication, defaults.",
                "/admin/settings",
            ),
            admin_tile(
                "Billing", "Plans, invoices, payment methods.", "/admin/billing"
            ),
            admin_tile("Regions", "Add / remove regions and quotas.", "/admin/regions"),
            admin_tile("Users", "Invite, roles, permissions.", "/admin/users"),
            admin_tile("Activity", "Audit logs and recent actions.", "/admin/activity"),
            columns="3",  # responsive: 1col (mobile), 2col (tablet), 3col (desktop)
            gap="16px",
            width="100%",
        ),
        spacing="4",
        padding="24px",
        max_width="1000px",
        align="start",
        margin_x="auto",
    )


@rx.page(
    route="/admin",
    title="Admin",
    on_load=AuthState.check_login,
)
@template
def admin():
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
