import reflex as rx

from ..state.auth import AuthState


class State(rx.State):
    query: str = ""

    def on_enter(self, event):
        # event.key is the name of the key pressed
        if event == "Enter":
            # return is important so Reflex knows to dispatch the inner event
            return AuthState.login


@rx.page(route="/auth/callback", on_load=AuthState.callback)
def callback() -> rx.Component:
    return rx.container()


@rx.page(route="/login", title="Login")
def login():
    return rx.flex(
        rx.card(
            rx.vstack(
                rx.center(
                    rx.image(
                        src="/logo.png",
                        width="10em",
                        height="auto",
                    ),
                    rx.heading(
                        "Sign in to your account",
                        size="6",
                        as_="h2",
                        text_align="center",
                        width="100%",
                    ),
                    direction="column",
                    spacing="5",
                    width="100%",
                ),
                rx.button(
                    "Log in with SSO",
                    on_click=AuthState.login_redirect,
                    size="3",
                    width="100%",
                ),
                spacing="6",
                width="100%",
            ),
            size="4",
            max_width="28em",
            width="100%",
        ),
        class_name="flex-row justify-center items-center h-screen w-screen",
    )
