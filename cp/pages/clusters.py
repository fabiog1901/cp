import asyncio
import json

import reflex as rx

from .. import db
from ..components.BadgeClusterStatus import get_cluster_status_badge
from ..cp import app
from ..models import Cluster, ClusterOverview, StrID, WebUser
from ..state.base import BaseState
from ..template import template
from ..util import get_funny_name

chip_props = {
    "radius": "full",
    "variant": "surface",
    "size": "3",
    "cursor": "pointer",
    "style": {"_hover": {"opacity": 0.75}},
}


disk_sizes = ["500 GB", "1 TB", "2 TB"]


def multi_selected_item_chip(item: str) -> rx.Component:
    return rx.badge(
        rx.match(
            item[:3],
            ("aws", rx.image("/aws.png", width="35px", height="auto")),
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


def multi_unselected_item_chip(item: StrID) -> rx.Component:
    return rx.cond(
        State.selected_regions.contains(item.id),
        rx.fragment(),
        rx.badge(
            rx.match(
                item.id[:3],
                ("aws", rx.image("/aws.png", width="30px", height="auto")),
                ("gcp", rx.image("/gcp.png", width="30px", height="auto")),
                ("azr", rx.image("/azr.png", width="35px", height="auto")),
                ("vmw", rx.image("/vmw.png", width="30px", height="auto")),
            ),
            item.id[4:],
            rx.icon("circle-plus", size=18),
            color_scheme="gray",
            **chip_props,
            on_click=State.multi_add_selected(item.id),
        ),
    )


def region_selector() -> rx.Component:
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
            rx.foreach(State.regions, multi_unselected_item_chip),
            wrap="wrap",
            spacing="2",
            justify_content="start",
        ),
        justify_content="start",
        align_items="start",
        width="100%",
    )


# SINGLE SELECT CPU


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
            rx.foreach(State.cpus_per_node, item_chip),
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


class State(BaseState):
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

    # CREATE NEW CLUSTER DIALOG PARAMETERS
    selected_cpu: int = None
    selected_disk: str = disk_sizes[0]
    selected_name: str = get_funny_name()
    versions: list[str] = []
    regions: list[StrID] = []
    version: str = ""
    cluster_group: str = ""
    nodes_per_region: list[str] = []
    cpus_per_node: list[int] = []

    @rx.event
    def load_funny_name(self):
        self.selected_name = get_funny_name()

    sort_value = ""
    search_value = ""
    is_running: bool = False

    @rx.event(background=True)
    async def fetch_all_clusters(self):
        if self.is_running:
            return
        async with self:
            # fetch this data only once
            self.versions = [x.id for x in db.get_versions()]
            self.version = self.versions[0]

            self.nodes_per_region = [x.id for x in db.get_nodes_per_region()]
            self.node_count = int(self.nodes_per_region[0])

            self.cpus_per_node = [x.id for x in db.get_cpus_per_node()]
            self.selected_cpu = self.cpus_per_node[0]

            self.regions = db.get_regions()

            self.cluster_group = self.webuser.groups[0]
            self.is_running = True

        while True:
            if (
                self.router.page.path != "/clusters"
                or self.router.session.client_token
                not in app.event_namespace.token_to_sid
            ):
                print("clusters.py: Stopping background task.")
                async with self:
                    self.is_running = False
                break

            async with self:
                # NOTE for some reason, `groups` has to be casted to a list
                # even though it's already a list[str]
                self.clusters = db.get_all_clusters(list(self.webuser.groups))

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
        form_data["regions"] = list(self.selected_regions)
        form_data["version"] = self.version
        form_data["group"] = self.cluster_group

        print(form_data)
        msg_id: StrID = db.insert_into_mq(
            "CREATE_CLUSTER", form_data, self.webuser.username
        )
        db.insert_event_log(
            self.webuser.username, "CREATE_CLUSTER", form_data | {"job_id": msg_id.id}
        )

        self.selected_cpu = self.cpus_per_node[0]
        self.selected_disk = disk_sizes[0]
        self.selected_regions = []
        self.selected_name = get_funny_name()
        return rx.toast.info(f"Job {msg_id.id} requested.")

    @rx.event
    def delete_cluster(self, cluster_id: str):
        msg_id: StrID = db.insert_into_mq(
            "DELETE_CLUSTER",
            {"cluster_id": cluster_id},
            self.webuser.username,
        )
        db.insert_event_log(
            self.webuser.username,
            "DELETE_CLUSTER",
            {"cluster_id": cluster_id, "job_id": msg_id.id},
        )
        return rx.toast.info(f"Job {msg_id.id} requested.")


def new_cluster_dialog():
    return rx.cond(
        (BaseState.webuser.role == "admin") | (BaseState.webuser.role == "rw"),
        rx.dialog.root(
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
                        rx.hstack(
                            cpu_item_selector(),
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("database", size=20),
                                    rx.heading("Nodes per Region", size="4"),
                                    spacing="2",
                                    align="center",
                                    width="100%",
                                ),
                                rx.radio(
                                    State.nodes_per_region,
                                    on_change=State.set_node_count,
                                    default_value="3",
                                    direction="row",
                                    color_scheme="mint",
                                ),
                            ),
                        ),
                        rx.divider(),
                        disk_item_selector(),
                        rx.divider(),
                        region_selector(),
                        rx.divider(),
                        rx.hstack(
                            rx.vstack(
                                rx.heading("CockroachDB version", size="4"),
                                rx.select(
                                    State.versions,
                                    value=State.version,
                                    on_change=State.set_version,
                                    color_scheme="mint",
                                    required=True,
                                    class_name="min-w-64"
                                ),
                                class_name="min-w-64",
                            ),
                            rx.spacer(),
                            rx.vstack(
                                rx.heading("Cluster group", size="4"),
                                rx.select(
                                    State.webuser.groups,
                                    value=State.cluster_group,
                                    on_change=State.set_cluster_group,
                                    color_scheme="mint",
                                    required=True,
                                    class_name="min-w-64"
                                ),
                                class_name="min-w-64",
                            ),
                        ),
                        rx.divider(),
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
                    on_submit=lambda form_data: State.create_new_cluster(
                        form_data, BaseState.webuser
                    ),
                    reset_on_submit=False,
                ),
                max_width="850px",
            ),
        ),
        rx.tooltip(
            rx.button(
                rx.icon("plus"),
                rx.text("New Cluster"),
                disabled=True,
                class_name="cursor-pointer",
            ),
            content="You need to have admin or rw role to create new clusters",
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
        # GROUP
        rx.table.cell(cluster.grp),
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
                    rx.cond(
                        (BaseState.webuser.role == "admin")
                        | (BaseState.webuser.role == "rw"),
                        rx.alert_dialog.root(
                            rx.alert_dialog.trigger(
                                rx.box(
                                    rx.tooltip(
                                        rx.icon(
                                            "trash-2",
                                            color=None,
                                            size=30,
                                            class_name="cursor-pointer text-red-500 hover:text-red-300",
                                        ),
                                        content="Delete the cluster",
                                    ),
                                ),
                            ),
                            rx.alert_dialog.content(
                                rx.alert_dialog.title(cluster.cluster_id),
                                rx.alert_dialog.description(
                                    size="2",
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
                                            "Delete Cluster",
                                            color_scheme="red",
                                            variant="solid",
                                            on_click=lambda: State.delete_cluster(
                                                cluster.cluster_id,
                                            ),
                                        ),
                                    ),
                                    spacing="3",
                                    margin_top="16px",
                                    justify="end",
                                ),
                                style={"max_width": 450},
                            ),
                        ),
                        rx.tooltip(
                            rx.icon(
                                "trash-2",
                                size=30,
                                color="gray",
                            ),
                            content="You need to have admin or rw role to delete a cluster",
                        ),
                    ),
                    rx.cond(
                        (BaseState.webuser.role == "admin")
                        | (BaseState.webuser.role == "rw"),
                        rx.tooltip(
                            rx.icon(
                                "circle-fading-arrow-up",
                                color=None,
                                size=30,
                                class_name="cursor-pointer text-green-500 hover:text-green-300",
                            ),
                            content="Upgrade the cluster",
                        ),
                        rx.tooltip(
                            rx.icon(
                                "circle-fading-arrow-up",
                                color="gray",
                                size=30,
                            ),
                            content="You need to have admin or rw role to upgrade a cluster",
                        ),
                    ),
                    rx.cond(
                        (BaseState.webuser.role == "admin")
                        | (BaseState.webuser.role == "rw"),
                        rx.tooltip(
                            rx.icon(
                                "bug-play",
                                size=30,
                                color=None,
                                class_name="cursor-pointer text-blue-500 hover:text-blue-300",
                            ),
                            content="Debug the cluster",
                        ),
                        rx.tooltip(
                            rx.icon(
                                "bug-play",
                                color="gray",
                                size=30,
                            ),
                            content="You need to have admin or rw role to debug a cluster",
                        ),
                    ),
                    spacing="6",
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
                    rx.table.column_header_cell("Group"),
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


@rx.page(
    route="/clusters",
    title="Clusters",
    on_load=BaseState.check_login,
)
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
        on_mount=rx.cond(
            BaseState.is_logged_in,
            State.fetch_all_clusters(BaseState.webuser),
            BaseState.just_return,
        ),
    )
