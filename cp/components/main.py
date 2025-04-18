import reflex as rx


def status_badge(state):
    return rx.text(
        state,
        bg="green.100",
        color="green.800",
        font_size="0.8em",
        px="2",
        py="0.5",
        border_radius="md",
        font_weight="bold",
    )


def version_link(version, note=None):
    return rx.link(
        version + (" " + note if note else ""),
        href="#",
        color="blue.500",
        text_decoration="underline",
    )


def action_menu():
    return rx.button("⋯", variant="ghost", size="4")


import reflex as rx


def user_profile_menu():
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                rx.icon("user"),
                class_name="mx-2",
            )
        ),
        rx.menu.content(
            rx.menu.item("Edit", shortcut="⌘ E"),
            rx.menu.item("Duplicate", shortcut="⌘ D"),
            rx.menu.separator(),
            rx.menu.item("Archive", shortcut="⌘ N"),
            rx.menu.sub(
                rx.menu.sub_trigger("More"),
                rx.menu.sub_content(
                    rx.menu.item("Move to project…"),
                    rx.menu.item("Move to folder…"),
                    rx.menu.separator(),
                    rx.menu.item("Advanced options…"),
                ),
            ),
            rx.menu.separator(),
            rx.menu.item("Share"),
            rx.menu.item("Add to favorites"),
            rx.menu.separator(),
            rx.menu.item("Delete", shortcut="⌘ ⌫", color="red"),
        ),
    )
