import asyncio

import reflex as rx
# MULTISELECT
from reflex.components.radix.themes.base import LiteralAccentColor

from .. import db
from ..components.BadgeClusterStatus import get_cluster_status_badge
from ..cp import app
from ..models import Cluster, ClusterOverview, MsgID
from ..template import template
from ..util import get_funny_name

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
        # on_click=State.setvar("selected_cpu", ""),
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
        on_click=State.setvar("selected_disk", item),
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

    selected_cpu: int = cpu_sizes[0]
    selected_disk: str = disk_sizes[0]
    selected_name: str = get_funny_name()

    @rx.event
    def load_funny_name(self):
        self.selected_name = get_funny_name()

    sort_value = ""
    search_value = ""
    bg_task: bool = False

    @rx.event(background=True)
    async def fetch_all_clusters(self):
        if self.bg_task:
            return
        async with self:
            self.bg_task = True

        while True:
            # if self.router.session.client_token not in app.event_namespace.token_to_sid:
            if self.router.page.path != "/clusters":
                print("clusters.py: Stopping background task.")
                async with self:
                    self.bg_task = False
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

    node_count: int = 3

    @rx.event
    def set_node_count(self, item: str):
        self.node_count = int(item)

    @rx.event
    def create_new_cluster(self, form_data: dict):
        form_data["node_cpus"] = self.selected_cpu

        form_data["disk_size"] = {
            "500 GB": 500,
            "1 TB": 1000,
            "2 TB": 2000,
        }.get(self.selected_disk, "500")

        form_data["node_count"] = int(self.node_count)
        form_data["regions"] = self.selected_regions

        msg_id: MsgID = db.insert_msg("CREATE_CLUSTER", form_data, "fabio")
        self.selected_cpu = cpu_sizes[0]
        self.selected_disk = disk_sizes[0]
        self.selected_regions = []
        return rx.toast.info(f"Job {msg_id.msg_id} requested.")

    @rx.event
    def delete_cluster(self, cluster_id: str):
        msg_id: MsgID = db.insert_msg(
            "DELETE_CLUSTER", {"cluster_id": cluster_id}, "fabio"
        )

        return rx.toast.info(f"Job {msg_id.msg_id} requested.")


def new_cluster_dialog():
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus"), rx.text("New Cluster"), class_name="cursor-pointer"
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Create New Cluster", class_name="text-4xl pb-4"),
            rx.form(
                rx.flex(
                    rx.heading("Cluster Name", size="4"),
                    rx.input(
                        placeholder="Name",
                        name="name",
                        default_value=State.selected_name,
                        on_mount=State.load_funny_name,
                        color_scheme="mint",
                        class_name="",
                    ),
                    rx.divider(),
                    cpu_item_selector(),
                    rx.divider(),
                    rx.hstack(
                        rx.icon("database", size=20),
                        rx.heading("Nodes per Region", size="4"),
                        spacing="2",
                        align="center",
                        width="100%",
                    ),
                    rx.radio(
                        ["1", "2", "3", "4", "5", "6", "7", "8"],
                        on_change=State.set_node_count,
                        default_value="3",
                        direction="row",
                        color_scheme="mint",
                    ),
                    rx.divider(),
                    disk_item_selector(),
                    rx.divider(),
                    multi_items_selector(),
                    rx.heading("CockroachDB version", size="4"),
                    rx.input(
                        name="version",
                        placeholder="latest",
                        default_value="latest",
                        color_scheme="mint",
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
        # CLUSTER_ID
        rx.table.cell(
            rx.link(
                rx.text(cluster.cluster_id, class_name="text-2xl font-semibold"),
                href=f"/clusters/{cluster.cluster_id}",
            )
        ),
        # CREATED BY
        rx.table.cell(cluster.created_by),
        # STATUS
        rx.table.cell(get_cluster_status_badge(cluster.status)),
        # ACTION
        rx.table.cell(
            rx.match(
                cluster.status,
                ("DELETED", rx.box()),
                ("DELETING...", rx.box()),
                rx.hstack(
                    rx.tooltip(
                        rx.icon(
                            "trash-2",
                            color="gray",
                            on_click=lambda: State.delete_cluster(cluster.cluster_id),
                        ),
                        content="Delete the cluster",
                    ),
                    rx.tooltip(
                        rx.icon(
                            "circle-fading-arrow-up",
                            color="gray",
                            on_click=lambda: State.delete_cluster(cluster.cluster_id),
                        ),
                        content="Upgrade the cluster",
                    ),
                    rx.tooltip(
                        rx.icon(
                            "bug-play",
                            color="gray",
                            on_click=lambda: State.delete_cluster(cluster.cluster_id),
                        ),
                        content="Debug the cluster",
                    ),
                ),
            )
        ),
    )


def clusters_table():
    return rx.vstack(
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
        size="3",
    )


@rx.page(route="/clusters", title="Clusters", on_load=State.fetch_all_clusters)
@template
def clusters():
    return rx.flex(
        rx.text(
            "Clusters",
            class_name="p-2 text-8xl font-semibold",
        ),
        rx.hstack(new_cluster_dialog(), direction="row-reverse", class_name="p-4"),
        rx.flex(clusters_table(), class_name="flex-1 flex-col overflow-y-scroll p-2"),
        class_name="flex-1 flex-col overflow-hidden",
    )
