import asyncio

import reflex as rx

from ...backend import db
from ...cp import app
from ...models import TS_FORMAT, EventType, Setting
from ...state import AuthState
from ...template import template


class State(AuthState):
    settings: list[Setting] = []

    original: dict[str, str] = {}

    draft: dict[str, str] = {}

    def set_field(self, id: str, value: str):
        self.draft[id] = value

    def save(self, id):
        db.set_setting(id, self.draft[id], self.webuser.username)
        db.insert_event_log(
            self.webuser.username,
            EventType.UPDATE_SETTING,
            {"ID": id, "value": self.draft[id]},
        )
        self.original[id] = self.draft[id]

    def discard(self, id):
        self.draft[id] = self.original[id]

    @rx.var
    def is_dirty(self) -> bool:
        return self.draft != self.original

    is_running: bool = False
    has_copied: bool = False

    @rx.event(background=True)
    async def start_bg_event(self):
        if self.is_running:
            return
        async with self:
            self.is_running = True

        while True:
            if (
                self.router.page.path != "/admin/settings"
                or self.router.session.client_token
                not in app.event_namespace.token_to_sid
            ):
                print("settings.py: Stopping background task.")
                async with self:
                    self.is_running = False
                    self.has_copied = False
                    self.draft = {}
                break

            async with self:
                self.settings = db.fetch_all_settings()

                self.original = {item.id: item.value for item in self.settings}
                if not self.has_copied:
                    self.draft: dict = self.original.copy()
                    self.has_copied = True
            await asyncio.sleep(5)


def config_editor_page() -> rx.Component:
    return rx.flex(
        rx.foreach(
            State.settings,
            lambda item: rx.hstack(
                rx.text(item.id, class_name="w-80 font-semibold"),
                rx.cond(
                    State.original[item.id] != State.draft[item.id],
                    rx.input(
                        value=State.draft[item.id],
                        on_change=lambda v: State.set_field(item.id, v),
                        class_name="w-80 text-red-300",
                    ),
                    rx.input(
                        value=State.draft[item.id],
                        on_change=lambda v: State.set_field(item.id, v),
                        class_name="w-80",
                    ),
                ),
                rx.moment(item.updated_at, format=TS_FORMAT, class_name="w-48"),
                rx.text(item.updated_by, class_name="w-24"),
                rx.text(item.default_value, class_name="w-32"),
                rx.text(item.description, class_name="w-80"),
                rx.cond(
                    State.original[item.id] != State.draft[item.id],
                    rx.hstack(
                        rx.icon(
                            "check",
                            size=30,
                            stroke_width=2.5,
                            on_click=State.save(item.id),
                            class_name="border-2 rounded-full p-1 border-green-500 hover:border-green-300 cursor-pointer text-green-500 hover:text-green-300",
                        ),
                        rx.icon(
                            "x",
                            size=30,
                            stroke_width=2.5,
                            on_click=State.discard(item.id),
                            class_name="border-2  rounded-full p-1 border-red-500 hover:border-red-300 cursor-pointer text-red-500 hover:text-red-300",
                        ),
                    ),
                    rx.box(),
                ),
                class_name="p-2",
            ),
        ),
        class_name="flex-1 flex-col overflow-y-scroll pt-8",
    )


@rx.page(
    route="/admin/settings",
    title="Settings",
    on_load=AuthState.check_login,
)
@template
def webpage():
    return rx.cond(
        AuthState.is_admin,
        rx.flex(
            rx.hstack(
                rx.text("ID", class_name="w-80 font-semibold"),
                rx.text("Value", class_name="font-semibold w-80"),
                rx.text("Updated_at", class_name="font-semibold w-48"),
                rx.text("Updated by", class_name="font-semibold w-24"),
                rx.text("Default", class_name="font-semibold w-32"),
                rx.text("Description", class_name="font-semibold w-80"),
                class_name="p-2",
            ),
            config_editor_page(),
            class_name="flex-1 flex-col overflow-hidden",
            on_mount=State.start_bg_event,
        ),
        rx.text(
            "Not Authorized",
        ),
    )
