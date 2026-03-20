import logging
from typing import get_args

import reflex as rx
import yaml
from reflex.components.radix.themes.base import LiteralAccentColor

from ...services import events
from ...services.errors import ServiceError
from ..components.notify import NotifyState
from ...models import TS_FORMAT, EventLogYaml
from ..state import AuthState
from ..layouts.template import template

ROUTE = "/events"
logger = logging.getLogger(__name__)


class State(AuthState):

    events: list[EventLogYaml] = []

    colors: list[str] = list(get_args(LiteralAccentColor))

    total_items: int
    offset: int = 0
    limit: int = 20

    @rx.var(cache=True)
    def page_number(self) -> int:
        return (self.offset // self.limit) + 1 + (1 if self.offset % self.limit else 0)

    @rx.var(cache=True)
    def total_pages(self) -> int:
        return self.total_items // self.limit + (
            1 if self.total_items % self.limit else 0
        )

    @rx.event
    def prev_page(self):
        self.offset = max(self.offset - self.limit, 0)
        self.load_data()

    @rx.event
    def next_page(self):
        if self.offset + self.limit < self.total_items:
            self.offset += self.limit
        self.load_data()

    @rx.event
    def load_data(self):
        """Get all users from the database."""

        try:
            all_events = events.list_visible_events(
                self.limit,
                self.offset,
                list(self.webuser.groups),
                self.is_admin,
            )
        except ServiceError as err:
            return NotifyState.show(err.user_title, err.user_message)
        except Exception:
            logger.exception("Unexpected error while loading events")
            return NotifyState.show(
                "Error",
                "Unable to load events right now.",
            )

        self.events = [
            EventLogYaml(
                created_at=x.created_at,
                created_by=x.created_by,
                event_type=x.event_type,
                event_details_yaml=yaml.dump(x.event_details),
            )
            for x in all_events
        ]

        try:
            self.total_items = events.get_event_total()
        except ServiceError as err:
            return NotifyState.show(err.user_title, err.user_message)
        except Exception:
            logger.exception("Unexpected error while loading event count")
            return NotifyState.show(
                "Error",
                "Unable to load the event count right now.",
            )


def table_row(event: EventLogYaml):
    return rx.table.row(
        rx.table.cell(
            rx.moment(
                event.created_at,
                format=TS_FORMAT,
                tz="UTC",
            ),
            class_name="min-w-6xl",
        ),
        rx.table.cell(event.created_by),
        rx.table.cell(
            rx.badge(
                event.event_type,
                color_scheme=State.colors[
                    event.event_type.length() % State.colors.length()
                ],
                variant="solid",
                size="3",
            )
        ),
        rx.table.cell(
            rx.code_block(
                event.event_details_yaml,
                language="yaml",
                show_line_numbers=False,
            ),
        ),
    )


def data_table():
    return rx.vstack(
        rx.hstack(
            rx.button(
                "Prev",
                on_click=State.prev_page,
            ),
            rx.text(f"Page {State.page_number} / {State.total_pages}"),
            rx.button(
                "Next",
                on_click=State.next_page,
            ),
            class_name="p-2",
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Timestamp"),
                    rx.table.column_header_cell("Username"),
                    rx.table.column_header_cell("Event Type"),
                    rx.table.column_header_cell("Event Details"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.events,
                    table_row,
                )
            ),
            width="100%",
            size="3",
        ),
        width="100%",
    )


@rx.page(
    route=ROUTE,
    title="Events",
    on_load=AuthState.check_login,
)
@template
def webpage():
    return rx.cond(
        AuthState.is_admin,
        rx.flex(
            rx.text(
                "Events",
                class_name="p-2 text-8xl font-semibold",
            ),
            rx.vstack(
                data_table(),
                class_name="flex-1 flex-col overflow-y-scroll pt-8",
            ),
            class_name="flex-1 flex-col overflow-hidden",
            on_mount=State.load_data,
        ),
        rx.text(
            "Not Authorized",
        ),
    )
