import reflex as rx


def get_job_status_badge(status: str) -> rx.Component:
    return (
        rx.match(
            status,
            (
                "RUNNING",
                rx.badge(
                    "RUNNING...",
                    class_name="rounded animate-pulse bg-orange-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            (
                "COMPLETED",
                rx.badge(
                    "COMPLETED",
                    class_name="rounded bg-green-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            (
                "FAILED",
                rx.badge(
                    "FAILED",
                    class_name="rounded bg-red-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            (
                "PENDING",
                rx.badge(
                    "PENDING...",
                    class_name="rounded animate-pulse bg-purple-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            (
                "ABORTED",
                rx.badge(
                    "ABORTED",
                    class_name="rounded bg-gray-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            rx.badge(
                status,
                class_name="rounded bg-blue-600 text-white px-4 text-xl font-semibold",
            ),
        ),
    )
