import reflex as rx


def get_event_type_badge(event_type: str) -> rx.Component:
    return (
        rx.match(
            event_type,
            (
                "LOGIN",
                rx.badge(
                    "LOGIN",
                    class_name="rounded bg-green-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            (
                "LOGOUT",
                rx.badge(
                    "LOGOUT",
                    class_name="rounded bg-gray-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            (
                "CREATE_CLUSTER",
                rx.badge(
                    "CREATE_CLUSTER",
                    class_name="rounded bg-orange-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            (
                "DELETE_CLUSTER",
                rx.badge(
                    "DELETE_CLUSTER",
                    class_name="rounded bg-red-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            (
                "SCALE_CLUSTER",
                rx.badge(
                    "SCALE_CLUSTER",
                    class_name="rounded bg-yellow-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            (
                "UPGRADE_CLUSTER",
                rx.badge(
                    "UPGRADE_CLUSTER",
                    class_name="rounded bg-purple-600 text-white px-4 text-xl font-semibold",
                ),
            ),
            rx.badge(
                event_type,
                class_name="rounded bg-blue-600 text-white px-4 text-xl font-semibold",
            ),
        ),
    )
