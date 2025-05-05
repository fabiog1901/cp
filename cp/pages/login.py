import reflex as rx

from ..state.auth import AuthState


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
                        on_blur=AuthState.set_username,
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
                        on_blur=AuthState.set_password,
                        size="3",
                        width="100%",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.button("Log in", on_click=AuthState.login, size="3", width="100%"),
                spacing="6",
                width="100%",
            ),
            size="4",
            max_width="28em",
            width="100%",
        ),
        class_name="flex-row justify-center items-center h-screen w-screen",
    )
