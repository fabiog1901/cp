import reflex as rx

from ..state.auth import AuthState


class State(rx.State):
    query: str = ""

    def on_enter(self, event):
        # event.key is the name of the key pressed
        if event == "Enter":
            # return is important so Reflex knows to dispatch the inner event
            return AuthState.login


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
                rx.vstack(
                    rx.text(
                        "Username",
                        size="3",
                        weight="medium",
                        text_align="left",
                        width="100%",
                    ),
                    rx.input(
                        placeholder="",
                        type="username",
                        on_change=AuthState.set_username,
                        size="3",
                        width="100%",
                    ),
                    justify="start",
                    spacing="2",
                    width="100%",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            "Password",
                            size="3",
                            weight="medium",
                        ),
                        rx.link(
                            "Forgot password?",
                            href="#",
                            size="3",
                        ),
                        justify="between",
                        width="100%",
                    ),
                    rx.input(
                        placeholder="Enter your password",
                        type="password",
                        on_change=AuthState.set_password,
                        on_key_down=State.on_enter,
                        size="3",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.button(
                    "Log in",
                    on_click=AuthState.login,
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
