# notify.py
import reflex as rx


class NotifyState(rx.State):
    dopen: bool = False
    title: str = ""
    message: str = ""

    def show(self, title: str, message: str):
        self.title = title
        self.message = message
        self.dopen = True

    def close(self):
        self.dopen = False


def notify_dialog() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title(NotifyState.title),
            rx.alert_dialog.description(NotifyState.message),
            rx.hstack(
                rx.button("OK", on_click=NotifyState.close),
                justify="end",
                spacing="3",
            ),
            max_width="420px",
            padding="20px",
            border_radius="12px",
        ),
        open=NotifyState.dopen,
        on_open_change=NotifyState.set_dopen,
    )
