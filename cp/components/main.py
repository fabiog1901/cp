import reflex as rx

from ..state.base import BaseState

chip_props = {
    "radius": "full",
    "variant": "surface",
    "size": "3",
    "cursor": "pointer",
    "style": {"_hover": {"opacity": 0.75}},
}


def item_selector(
    state: rx.State,
    state_options_var,
    state_selected_var,
    icon: str,
    title: str,
    var: str,
) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(icon, size=20),
            rx.heading(title, size="4"),
            spacing="2",
            align="center",
            width="100%",
        ),
        rx.hstack(
            rx.foreach(
                state_options_var,
                lambda item: rx.cond(
                    state_selected_var == item,
                    rx.badge(
                        rx.icon("check", size=18),
                        item,
                        color_scheme="mint",
                        **chip_props,
                        # on_click=State.setvar(var, ""),
                    ),
                    rx.badge(
                        item,
                        color_scheme="gray",
                        **chip_props,
                        on_click=state.setvar(var, item),
                    ),
                ),
            ),
            wrap="wrap",
            spacing="2",
        ),
        align_items="start",
        spacing="4",
        width="100%",
    )


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


def user_profile_menu():
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                rx.icon("user"),
                class_name="mx-2",
            )
        ),
        rx.menu.content(
            # rx.menu.item("Edit", shortcut="⌘ E"),
            # rx.menu.item("Duplicate", shortcut="⌘ D"),
            # rx.menu.separator(),
            # rx.menu.item("Archive", shortcut="⌘ N"),
            # rx.menu.sub(
            #     rx.menu.sub_trigger("More"),
            #     rx.menu.sub_content(
            #         rx.menu.item("Move to project…"),
            #         rx.menu.item("Move to folder…"),
            #         rx.menu.separator(),
            #         rx.menu.item("Advanced options…"),
            #     ),
            # ),
            # rx.menu.separator(),
            # rx.menu.item("Share"),
            # rx.menu.item("Add to favorites"),
            # rx.menu.separator(),
            rx.menu.item(
                "Logout", shortcut="⌘ ⌫", color="red", on_click=BaseState.logout
            ),
        ),
    )
