import reflex as rx


def get_cluster_status_badge(status: str) -> rx.Component:
    return rx.match(
        status,
        (
            "RUNNING",
            rx.badge(
                "RUNNING",
                class_name="rounded bg-green-600 text-white px-4 text-xl font-semibold",
            ),
        ),
        (
            "DELETE_FAILED",
            rx.badge(
                "DELETE FAILED",
                class_name="rounded bg-red-600 text-white px-4 text-xl font-semibold",
            ),
        ),
        (
            "DELETED",
            rx.badge(
                "DELETED",
                class_name="rounded bg-slate-600 text-white px-4 text-xl font-semibold",
            ),
        ),
        (
            "PROVISIONING",
            rx.badge(
                "PROVISIONING...",
                class_name="rounded animate-pulse bg-orange-600 text-white px-4 text-xl font-semibold",
            ),
        ),
        rx.badge(
            status,
            class_name="rounded bg-blue-600 text-white px-4 text-xl font-semibold",
        ),
    )
