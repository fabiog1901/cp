import reflex as rx
import asyncio


from ..template import template
from ..models import Cluster, ClusterOverview, MsgID
from ..cp import app
from .. import db


# MULTISELECT
from reflex.components.radix.themes.base import (
    LiteralAccentColor,
)

chip_props = {
    "radius": "full",
    "variant": "surface",
    "size": "3",
    "cursor": "pointer",
    "style": {"_hover": {"opacity": 0.75}},
}

regions = [
    "aws:us-east-1",
    "aws:us-east-2",
    "aws:ca-central-1",
    "gcp:us-east4",
    "azr:eastus",
    "vmw:TX",
    "vmw:VA",
    "vmw:PA",
    "vmw:NY",
]

disk_sizes = ["500 GB", "1 TB", "2 TB"]

def multi_action_button(
    icon: str,
    label: str,
    on_click: callable,
    color_scheme: LiteralAccentColor,
) -> rx.Component:
    return rx.button(
        rx.icon(icon, size=16),
        label,
        variant="soft",
        size="2",
        on_click=on_click,
        color_scheme=color_scheme,
        cursor="pointer",
    )


def multi_selected_item_chip(item: str) -> rx.Component:
    return rx.badge(
        rx.match(
                item[:3],
                ("aws", rx.image("/aws.png", width="30px", height="auto")),
                ("gcp", rx.image("/gcp.png", width="30px", height="auto")),
                ("azr", rx.image("/azr.png", width="35px", height="auto")),
                ("vmw", rx.image("/vmw.png", width="30px", height="auto")),
            ),
        item[4:],
        rx.icon("circle-x", size=18),
        color_scheme="green",
        **chip_props,
        on_click=State.multi_remove_selected(item),
    )


def multi_unselected_item_chip(item: str) -> rx.Component:
    return rx.cond(
        State.selected_regions.contains(item),
        rx.fragment(),
        rx.badge(
            rx.match(
                item[:3],
                ("aws", rx.image("/aws.png", width="30px", height="auto")),
                ("gcp", rx.image("/gcp.png", width="30px", height="auto")),
                ("azr", rx.image("/azr.png", width="35px", height="auto")),
                ("vmw", rx.image("/vmw.png", width="30px", height="auto")),
            ),
            item[4:],
            rx.icon("circle-plus", size=18),
            color_scheme="gray",
            **chip_props,
            on_click=State.multi_add_selected(item),
        ),
    )


def multi_items_selector() -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.hstack(
                rx.icon("earth", size=20),
                rx.heading(
                    "Regions" + f" ({State.selected_regions.length()})",
                    size="4",
                ),
                spacing="1",
                align="center",
                width="100%",
                justify_content=["end", "start"],
            ),
            justify="between",
            flex_direction=["column", "row"],
            align="center",
            spacing="2",
            margin_bottom="10px",
            width="100%",
        ),
        # Selected Items
        rx.flex(
            rx.foreach(
                State.selected_regions,
                multi_selected_item_chip,
            ),
            wrap="wrap",
            spacing="2",
            justify_content="start",
        ),
        rx.divider(),
        # Unselected Items
        rx.flex(
            rx.foreach(regions, multi_unselected_item_chip),
            wrap="wrap",
            spacing="2",
            justify_content="start",
        ),
        justify_content="start",
        align_items="start",
        width="100%",
    )


# SINGLE SELECT CPU

cpu_sizes = [4, 8, 16, 32]


def unselected_item(item: str) -> rx.Component:
    return rx.badge(
        item,
        color_scheme="gray",
        **chip_props,
        on_click=State.setvar("selected_cpu", item),
    )


def selected_item(item: str) -> rx.Component:
    return rx.badge(
        rx.icon("check", size=18),
        item,
        color_scheme="mint",
        **chip_props,
        #on_click=State.setvar("selected_cpu", ""),
    )


def item_chip(item: str) -> rx.Component:
    return rx.cond(
        State.selected_cpu == item,
        selected_item(item),
        unselected_item(item),
    )


def cpu_item_selector() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon("cpu", size=20),
            rx.heading("CPU:", size="4"),
            spacing="2",
            align="center",
            width="100%",
        ),
        rx.hstack(
            rx.foreach(cpu_sizes, item_chip),
            wrap="wrap",
            spacing="2",
        ),
        align_items="start",
        spacing="4",
        width="100%",
    )


# SINGLE SELECT DISK
disk_chip_props = {
    "radius": "full",
    "variant": "soft",
    "size": "3",
    "cursor": "pointer",
    "style": {"_hover": {"opacity": 0.75}},
}




def disk_unselected_item(item: str) -> rx.Component:
    return rx.badge(
        item,
        color_scheme="gray",
        **chip_props,
        on_click=State.setvar("selected_disk", item)
    )


def disk_selected_item(item: str) -> rx.Component:
    return rx.badge(
        rx.icon("check", size=18),
        item,
        color_scheme="mint",
        **chip_props,
        # on_click=State.setvar("selected_disk", ""),
    )


def disk_item_chip(item: str) -> rx.Component:
    return rx.cond(
        State.selected_disk == item,
        disk_selected_item(item),
        disk_unselected_item(item),
    )


def disk_item_selector() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon("hard-drive", size=20),
            rx.heading("Disk:", size="4"),
            spacing="2",
            align="center",
            width="100%",
        ),
        rx.hstack(
            rx.foreach(disk_sizes, disk_item_chip),
            wrap="wrap",
            spacing="2",
        ),
        align_items="start",
        spacing="4",
        width="100%",
    )


class State(rx.State):
    current_cluster: Cluster = None
    clusters: list[ClusterOverview] = []
    
    # dialog box vars
    selected_regions: list[str] = []

    @rx.event
    def multi_add_selected(self, item: str):
        self.selected_regions.append(item)

    @rx.event
    def multi_remove_selected(self, item: str):
        self.selected_regions.remove(item)

        
    selected_cpu: str = cpu_sizes[0]
    selected_disk: str = disk_sizes[0]

        
    sort_value = ""
    search_value = ""

    @rx.event(background=True)
    async def fetch_all_clusters(self):
        while True:
            # if self.router.session.client_token not in app.event_namespace.token_to_sid:
            if self.router.page.path != "/clusters":
                print("clusters.py: Stopping background task.")
                break

            async with self:
                self.clusters = db.get_all_clusters()
            await asyncio.sleep(5)

    @rx.var(cache=True)
    def table_clusters(self) -> list[ClusterOverview]:
        clusters = self.clusters

        if self.sort_value != "":
            clusters = sorted(
                clusters,
                key=lambda user: getattr(user, self.sort_value).lower(),
            )

        if self.search_value != "":
            clusters = [
                cluster
                for cluster in clusters
                if any(
                    self.search_value.lower() in getattr(cluster, attr).lower()
                    for attr in [
                        "cluster_id",
                        "email",
                        "group",
                    ]
                )
            ]
        return clusters

    @rx.event
    def create_new_cluster(self, form_data: dict):
               
        form_data['node_cpus'] = self.selected_cpu
        
        form_data['disk_size'] = {
            "500 GB": 500,
            "1 TB": 1000,
            "2 TB": 2000
        }.get(self.selected_disk, "500")
        
        form_data['regions'] = self.selected_regions
        
        msg_id: MsgID = db.insert_msg("CREATE_CLUSTER", form_data, "fabio")
        return rx.toast.info(f"Job {msg_id.msg_id} requested.")


def new_cluster_dialog():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus"),
                rx.text("New Cluster"),
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(
                "Create New Cluster",
            ),
            rx.form(
                rx.flex(
                    rx.heading("Cluster Name", size="4"),
                    rx.input(placeholder="Name", name="name", default_value="fab"),
                    cpu_item_selector(),
                    rx.heading("Nodes per region", size="4"),
                    rx.input(name="node_count", default_value="3"),
                    disk_item_selector(),
                    multi_items_selector(),
                    rx.heading("CockroachDB version", size="4"),
                    rx.input(
                        name="version", placeholder="latest", default_value="latest"
                    ),
                    rx.flex(
                        rx.dialog.close(
                            rx.button(
                                "Cancel",
                                variant="soft",
                                color_scheme="gray",
                            ),
                        ),
                        rx.dialog.close(
                            rx.button("Submit", type="submit"),
                        ),
                        spacing="3",
                        justify="end",
                    ),
                    direction="column",
                    spacing="4",
                ),
                on_submit=State.create_new_cluster,
                reset_on_submit=False,
            ),
            max_width="450px",
        ),
    )


def get_cluster_row(cluster: Cluster):
    """Show a cluster in a table row."""
    return rx.table.row(
        rx.table.cell(
            rx.link(
                cluster.cluster_id,
                href=f"/clusters/{cluster.cluster_id}",
            )
        ),
        rx.table.cell(cluster.created_by),
        rx.table.cell(
            rx.match(
                cluster.status,
                ("OK", rx.icon("circle-check", color="green")),
                ("WARNING", rx.icon("triangle-alert", color="yellow")),
                rx.icon("circle-help"),
            )
        ),
        rx.table.cell(
            rx.link(
                rx.icon("trash-2", color="gray"),
                # on_click=lambda: State.bingo(cluster.cluster_id),
            )
        ),
    )


def clusters_table():
    return rx.vstack(
        rx.hstack(
            rx.select(
                ["cluster_id", "email", "group"],
                placeholder="Sort By: cluster_id",
                on_change=State.set_sort_value,
            ),
            rx.input(
                placeholder="Search here...",
                on_change=State.set_search_value,
            ),
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Name"),
                    rx.table.column_header_cell("Created By"),
                    rx.table.column_header_cell("Status"),
                    rx.table.column_header_cell("Actions"),
                ),
            ),
            rx.table.body(
                rx.foreach(
                    State.table_clusters,
                    get_cluster_row,
                )
            ),
            width="100%",
        ),
        rx.text(f"Showing {State.clusters.length()} clusters"),
        width="100%",
    )


@rx.page(route="/clusters", title="Clusters", on_load=State.fetch_all_clusters)
@template
def clusters():
    return rx.flex(
        rx.hstack(
            new_cluster_dialog(),
            direction="row-reverse",
        ),
        clusters_table(),
        class_name="flex-1 flex-col overflow-y-scroll p-2",
    )
