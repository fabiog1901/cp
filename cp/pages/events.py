import asyncio

import reflex as rx
import yaml

from ..backend import db
from ..components.BadgeEventType import get_event_type_badge
from ..cp import app
from ..models import TS_FORMAT, EventLog, EventLogYaml
from ..state import AuthState
from ..template import template


class State(AuthState):

    events: list[EventLogYaml] = []

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

    def _get_total_items(self):
        """Return the total number of items in the Customer table."""
        self.total_items = db.get_event_count()

    @rx.event
    def load_data(self):
        """Get all users from the database."""
        self.events = [
            EventLogYaml(
                created_at=x.created_at,
                created_by=x.created_by,
                event_type=x.event_type,
                event_details_yaml=yaml.dump(x.event_details),
            )
            for x in db.fetch_all_events(
                self.limit,
                self.offset,
                list(self.webuser.groups),
                self.is_admin,
            )
        ]
        self._get_total_items()


def get_event_row(event: EventLogYaml):
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
        rx.table.cell(get_event_type_badge(event.event_type)),
        rx.table.cell(
            rx.code_block(
                event.event_details_yaml,
                language="yaml",
                show_line_numbers=False,
            ),
        ),
    )


def events_table():
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
                    get_event_row,
                )
            ),
            width="100%",
            size="3",
        ),
        width="100%",
    )


@rx.page(
    route="/events",
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
                events_table(),
                class_name="flex-1 flex-col overflow-y-scroll pt-8",
            ),
            class_name="flex-1 flex-col overflow-hidden",
            on_mount=State.load_data,
        ),
        rx.text(
            "Not Authorized",
        ),
    )
