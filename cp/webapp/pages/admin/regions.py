# app.py
import asyncio
from typing import List

import reflex as rx

from ...components.main import breadcrumb
from ...components.notify import NotifyState
from ....cp import app
from ....models import Region
from ....services import regions_service
from ...state import AuthState
from ...layouts.template import template

ROUTE = "/admin/regions"


class State(AuthState):

    regions: List[Region] = []

    # modal visibility
    dialog_open: bool = False

    # draft fields for new region
    cloud: str = ""
    region: str = ""
    zone: str = ""
    vpc_id: str = ""
    security_groups_text: str = ""  # comma-separated
    subnet: str = ""
    image: str = ""
    extras_text: str = ""  # JSON (optional)

    def open_dialog(self):
        # reset draft and open
        self.cloud = ""
        self.region = ""
        self.zone = ""
        self.vpc_id = ""
        self.security_groups_text = ""
        self.subnet = ""
        self.image = ""
        self.extras_text = ""

        self.dialog_open = True

    def close_dialog(self):
        self.dialog_open = False

    def remove_region(self, r: Region):
        try:
            regions_service.delete_region(r, self.webuser.username)
        except Exception as e:
            return NotifyState.show("Error", str(e))

    def submit_new_region(self):
        self.dialog_open = False

        try:
            regions_service.create_region(
                cloud=self.cloud,
                region=self.region,
                zone=self.zone,
                vpc_id=self.vpc_id,
                security_groups_text=self.security_groups_text,
                subnet=self.subnet,
                image=self.image,
                extras_text=self.extras_text,
                created_by=self.webuser.username,
            )
        except Exception as e:
            return NotifyState.show("Error", str(e))

    is_running: bool = False

    @rx.event(background=True)
    async def start_bg_event(self):
        if self.is_running:
            return
        async with self:
            self.is_running = True

        while True:
            if (
                self.router.page.path != ROUTE
                or self.router.session.client_token
                not in app.event_namespace.token_to_sid
            ):
                print(f"{ROUTE}: Stopping background task.")
                async with self:
                    self.is_running = False
                break

            async with self:
                try:
                    self.regions = regions_service.list_regions()
                except Exception as e:
                    self.is_running = False
                    return NotifyState.show("Error", str(e))

            await asyncio.sleep(5)


# ---- UI bits ----


def table_row(r: Region) -> rx.Component:
    return rx.table.row(
        rx.table.cell(r.cloud.upper()),
        rx.table.cell(r.region),
        rx.table.cell(r.zone),
        rx.table.cell(r.vpc_id),
        rx.table.cell(rx.foreach(r.security_groups, lambda x: rx.text(f"{x} "))),
        rx.table.cell(r.subnet),
        rx.table.cell(r.image),
        rx.table.cell(r.extras),
        rx.table.cell(remove_region_dialog(r)),
    )


def data_table() -> rx.Component:
    return rx.vstack(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Cloud"),
                    rx.table.column_header_cell("Region"),
                    rx.table.column_header_cell("Zone"),
                    rx.table.column_header_cell("VPC ID"),
                    rx.table.column_header_cell("Security Groups"),
                    rx.table.column_header_cell("Subnet"),
                    rx.table.column_header_cell("Image"),
                    rx.table.column_header_cell("Extras"),
                    rx.table.column_header_cell(""),
                )
            ),
            rx.table.body(
                rx.foreach(
                    State.regions,
                    table_row,
                )
            ),
            width="100%",
        ),
        rx.text(f"Showing {State.regions.length()} regions"),
        width="100%",
        size="3",
    )


def remove_region_dialog(r: Region) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            rx.box(
                rx.tooltip(
                    rx.icon(
                        "trash-2",
                        color=None,
                        size=30,
                        class_name="cursor-pointer text-red-500 hover:text-red-300",
                    ),
                    content="Remove region",
                ),
            ),
        ),
        rx.alert_dialog.content(
            rx.alert_dialog.title(f"Remove region '{r.cloud.upper()} {r.region}' ?"),
            rx.alert_dialog.description(
                " ",
                size="4",
            ),
            rx.flex(
                rx.alert_dialog.cancel(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                    ),
                ),
                rx.alert_dialog.action(
                    rx.button(
                        "Remove",
                        color_scheme="red",
                        variant="solid",
                        on_click=lambda: State.remove_region(r),
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            style={"max_width": 450},
        ),
    )


def add_region_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Add New Region"),
            rx.dialog.description("Fill in the details for the new region."),
            rx.vstack(
                rx.hstack(
                    rx.input(
                        value=State.cloud,
                        placeholder="cloud (e.g., aws, gcp, azure)",
                        on_change=State.set_cloud,
                        width="100%",
                    ),
                    rx.input(
                        value=State.region,
                        placeholder="region (e.g., us-east-1)",
                        on_change=State.set_region,
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.hstack(
                    rx.input(
                        value=State.zone,
                        placeholder="zone (e.g., us-east-1a)",
                        on_change=State.set_zone,
                        width="100%",
                    ),
                    rx.input(
                        value=State.vpc_id,
                        placeholder="vpc_id",
                        on_change=State.set_vpc_id,
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.input(
                    value=State.security_groups_text,
                    placeholder="security_groups (comma-separated)",
                    on_change=State.set_security_groups_text,
                    width="100%",
                ),
                rx.hstack(
                    rx.input(
                        value=State.subnet,
                        placeholder="subnet",
                        on_change=State.set_subnet,
                        width="100%",
                    ),
                    rx.input(
                        value=State.image,
                        placeholder="image (e.g., AMI or image name)",
                        on_change=State.set_image,
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                rx.input(
                    value=State.extras_text,
                    placeholder='extras (JSON object, e.g. {"owner":"team","tier":"gold"})',
                    on_change=State.set_extras_text,
                    rows=5,
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            rx.hstack(
                rx.button("Cancel", variant="surface", on_click=State.close_dialog),
                rx.button("OK", color_scheme="blue", on_click=State.submit_new_region),
                justify="end",
                spacing="3",
            ),
            max_width="720px",
            padding="20px",
        ),
        open=State.dialog_open,
        on_open_change=State.set_dialog_open,
    )


@rx.page(
    route=ROUTE,
    title="Regions",
    on_load=AuthState.check_login,
)
@template
def webpage() -> rx.Component:
    return rx.cond(
        AuthState.is_admin,
        rx.flex(
            breadcrumb("Admin", "/admin/", "Regions"),
            rx.hstack(
                rx.button("Add new region", on_click=State.open_dialog),
                direction="row-reverse",
                class_name="p-4",
            ),
            rx.flex(data_table(), class_name="flex-1 flex-col overflow-y-scroll p-2"),
            add_region_dialog(),
            class_name="flex-1 flex-col overflow-hidden",
            on_mount=State.start_bg_event,
        ),
        rx.text("Not Authorized"),
    )
