import reflex as rx
from .bg import pull_from_mq

app = rx.App(
    theme=rx.theme(
        appearance="inherit",
        has_background=True,
        radius="large",
        accent_color="orange",
    ),
)


app.register_lifespan_task(pull_from_mq)
