import asyncio

import reflex as rx

from .. import db
from ..components.BadgeClusterStatus import get_cluster_status_badge
from ..components.BadgeJobStatus import get_job_status_badge
from ..components.main import item_selector, chip_props
from ..cp import app
from ..models import TS_FORMAT, Cluster, Job, StrID
from ..state.base import BaseState
from ..template import template
from .clusters import State as ClusterState
from ..util import get_human_size


class State(BaseState):
    current_cluster: Cluster = None
    current_cluster_description: dict = {}
    current_cluster_regions: list[dict[str, str | list[str]]] = []
    current_cluster_lbs: list[dict[str, str]] = []

    @rx.event
    def multi_add_selected(self, item: str):
        self.selected_regions.append(item)

    @rx.event
    def multi_remove_selected(self, item: str):
        self.selected_regions.remove(item)

    # SCALE CLUSTER DIALOG PARAMETERS
    available_versions: list[str] = []
    available_regions: list[StrID] = []
    available_node_counts: list[int] = []
    available_cpus_per_node: list[int] = []
    disk_fmt_2_size_map: dict[str, int] = {}
    available_disk_sizes: list[str] = []

    selected_name: str = ""
    selected_cpus_per_node: int = None
    selected_node_count: int = None
    selected_disk_size: str = None
    selected_regions: list[str] = []
    selected_version: str = ""
    selected_group: str = ""

    @rx.event
    def scale_cluster(self, form_data: dict):
        form_data["name"] = self.current_cluster.cluster_id
        form_data["node_cpus"] = self.selected_cpus_per_node
        form_data["disk_size"] = self.disk_fmt_2_size_map[self.selected_disk_size]
        form_data["node_count"] = self.selected_node_count
        form_data["regions"] = list(self.selected_regions)

        msg_id: StrID = db.insert_into_mq(
            "SCALE_CLUSTER",
            form_data,
            self.webuser.username,
        )
        db.insert_event_log(
            self.webuser.username,
            "SCALE_CLUSTER",
            form_data | {"job_id": msg_id.id},
        )

        # self.selected_regions = []
        # self.selected_version = self.available_versions[0]
        # self.selected_node_count = self.available_node_counts[0]
        # self.selected_cpus_per_node = self.available_cpus_per_node[0]
        # self.selected_disk_size = self.available_disk_sizes[0].size_gb
        # self.selected_group = self.webuser.groups[0]

        return rx.toast.info(f"Job {msg_id.id} requested.")

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

    is_running: bool = False
    just_once: bool = True

    # self.selected_version = self.current_cluster.description.version
    # self.selected_node_count = len(self.current_cluster.description['cluster'][0]['nodes'])
    # self.selected_cpus_per_node = self.current_cluster.description['node_cpus']
    # self.selected_disk_size = self.current_cluster.description['disk_size']
    # self.available_regions = [StrID(x.get("cloud") + ":" + x.get("region")) for x in self.current_cluster.description['cluster']]

    @rx.event
    def load_cluster_data(self):
        if self.current_cluster:
            self.selected_version = self.current_cluster.description.get("version", "")
            self.selected_node_count = len(
                self.current_cluster.description["cluster"][0]["nodes"]
            )
            self.selected_cpus_per_node = self.current_cluster.description["node_cpus"]
            self.selected_disk_size = get_human_size(self.current_cluster.description["disk_size"])
            self.selected_regions = [
                x.get("cloud") + ":" + x.get("region")
                for x in self.current_cluster.description["cluster"]
            ]


    @rx.event(background=True)
    async def fetch_cluster(self):
        if self.is_running:
            return
        async with self:
            # fetch this data only once
            self.available_versions = [x.id for x in db.get_versions()]
            self.available_node_counts = [x.id for x in db.get_node_counts()]
            self.available_cpus_per_node = [x.id for x in db.get_cpus_per_node()]
            self.disk_fmt_2_size_map = {
                get_human_size(x.id): x.id for x in db.get_disk_sizes()
            }
            self.available_disk_sizes = list(self.disk_fmt_2_size_map.keys())
            # self.selected_disk_size = self.available_disk_sizes[0]
            self.available_regions = db.get_regions()
            self.is_running = True

        while True:
            if (
                self.router.page.path != "/clusters/[c_id]"
                or self.router.session.client_token
                not in app.event_namespace.token_to_sid
            ):
                print("cluster_overview.py: Stopping background task.")
                async with self:
                    self.is_running = False
                break

            async with self:
                cluster: Cluster = db.get_cluster(
                    self.cluster_id,
                    list(self.webuser.groups),
                    self.is_admin,
                )
                if cluster is None:
                    self.is_running = False
                    # TODO redirect is buggy
                    return rx.redirect("/404", replace=True)

                self.current_cluster_description = cluster.description
                self.current_cluster_regions = cluster.description.get("cluster", [])
                self.current_cluster_lbs = cluster.description.get("lbs", [])
                self.current_cluster = cluster

                if self.just_once and self.current_cluster_description:
                    self.just_once = False
                    self.selected_version = self.current_cluster.description.get(
                        "version", ""
                    )
                    self.selected_node_count = len(
                        self.current_cluster.description["cluster"][0]["nodes"]
                    )
                    self.selected_cpus_per_node = self.current_cluster.description[
                        "node_cpus"
                    ]
                    self.selected_disk_size = get_human_size(self.current_cluster.description[
                        "disk_size"
                    ])
                    self.selected_regions = [
                        x.get("cloud") + ":" + x.get("region")
                        for x in self.current_cluster.description["cluster"]
                    ]

            await asyncio.sleep(5)


chip_props = {
    "radius": "full",
    "variant": "surface",
    "size": "3",
    "cursor": "pointer",
    "style": {"_hover": {"opacity": 0.75}},
}


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
            rx.foreach(State.available_regions, multi_unselected_item_chip),
            wrap="wrap",
            spacing="2",
            justify_content="start",
        ),
        justify_content="start",
        align_items="start",
        width="100%",
    )


def scale_cluster_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.box(
                rx.tooltip(
                    rx.icon(
                        "expand",
                        color=None,
                        size=30,
                        class_name="cursor-pointer text-yellow-500 hover:text-red-300 mr-4",
                    ),
                    content="Scale the cluster",
                ),
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(f"Scale {State.cluster_id}", class_name="text-4xl pb-4"),
            rx.form(
                rx.flex(
                    rx.hstack(
                        item_selector(
                            State,
                            State.available_cpus_per_node,
                            State.selected_cpus_per_node,
                            icon="cpu",
                            title="CPU:",
                            var="selected_cpus_per_node",
                        ),
                        item_selector(
                            State,
                            State.available_node_counts,
                            State.selected_node_count,
                            icon="database",
                            title="Nodes Per Region:",
                            var="selected_node_count",
                        ),
                    ),
                    rx.divider(),
                    item_selector(
                        State,
                        State.available_disk_sizes,
                        State.selected_disk_size,
                        "hard-drive",
                        "Disk",
                        "selected_disk_size",
                    ),
                    rx.divider(),
                    region_selector(),
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
                on_submit=lambda form_data: State.scale_cluster(
                    form_data, BaseState.webuser
                ),
                reset_on_submit=False,
            ),
            max_width="850px",
            on_open_auto_focus=State.load_cluster_data,
        ),
    )


def cluster_sidebar() -> rx.Component:
    return rx.flex(
        rx.link(rx.text("Overview", class_name="py-2"), href="/"),
        rx.link(rx.text("SQL Shell", class_name="py-2"), href="/"),
        # rx.divider(),
        rx.heading("Data", class_name="pb-2 pt-8"),
        rx.link(rx.text("Databases", class_name="py-2"), href="/"),
        rx.link(rx.text("Backup and Restore", class_name="py-2"), href="/"),
        rx.link(rx.text("Migrations", class_name="py-2"), href="/"),
        # rx.divider(),
        rx.heading("Security", class_name="pb-2 pt-8"),
        rx.link(rx.text("SQL Users", class_name="py-2"), href="/"),
        rx.link(rx.text("Networking", class_name="py-2"), href="/"),
        # rx.divider(),
        rx.heading("Monitoring", class_name="pb-2 pt-8"),
        rx.link(rx.text("Tools", class_name="py-2"), href="/"),
        rx.link(rx.text("Metrics", class_name="py-2"), href="/"),
        rx.link(rx.text("SQL Activity", class_name="py-2"), href="/"),
        rx.link(rx.text("Insights", class_name="py-2"), href="/"),
        rx.link(rx.text("Jobs", class_name="py-2"), href="/"),
        class_name="border-r flex-col min-w-48 p-2",
    )


@rx.page(
    route="/clusters/[c_id]",
    on_load=BaseState.check_login,
)
@template
def cluster():
    return rx.flex(
        rx.hstack(
            rx.icon("boxes", size=100, class_name="p-2"),
            rx.text(
                State.current_cluster.cluster_id,
                class_name="p-2 text-8xl font-semibold",
            ),
            rx.divider(orientation="vertical", size="4", class_name="mx-8"),
            get_cluster_status_badge(State.current_cluster.status),
            rx.hstack(
                rx.vstack(
                    rx.text("Version"),
                    rx.text(
                        State.current_cluster_description.version,
                        class_name="text-3xl font-semibold",
                    ),
                    class_name="mx-16",
                    align="center",
                ),
                direction="row-reverse",
                class_name="p-4 flex-1",
            ),
            align="center",
        ),
        rx.flex(
            # cluster_sidebar(),
            rx.flex(
                rx.hstack(
                    rx.card(
                        rx.text("Cluster", class_name="text-2xl font-semibold"),
                        rx.divider(class_name="my-2"),
                        rx.foreach(
                            State.current_cluster_regions,
                            lambda x: rx.flex(
                                rx.badge(
                                    rx.match(
                                        x.cloud,
                                        (
                                            "aws",
                                            rx.image(
                                                "/aws.png",
                                                width="30px",
                                                height="auto",
                                            ),
                                        ),
                                        (
                                            "gcp",
                                            rx.image(
                                                "/gcp.png",
                                                width="30px",
                                                height="auto",
                                            ),
                                        ),
                                        (
                                            "azure",
                                            rx.image(
                                                "/azr.png",
                                                width="35px",
                                                height="auto",
                                            ),
                                        ),
                                        (
                                            "vmw",
                                            rx.image(
                                                "/vmw.png",
                                                width="30px",
                                                height="auto",
                                            ),
                                        ),
                                    ),
                                    rx.text(x.region),
                                    class_name="text-lg p-2",
                                ),
                                rx.list.unordered(
                                    rx.foreach(
                                        x.nodes,
                                        lambda z: rx.list.item(z, class_name="p-2"),
                                    )
                                ),
                                class_name="flex-col",
                            ),
                        ),
                        class_name="min-w-80 min-h-96",
                    ),
                    rx.card(
                        rx.text("Load Balancers", class_name="text-2xl font-semibold"),
                        rx.divider(class_name="my-2"),
                        rx.foreach(
                            State.current_cluster_lbs,
                            lambda x: rx.flex(
                                rx.badge(
                                    rx.match(
                                        x.cloud,
                                        (
                                            "aws",
                                            rx.image(
                                                "/aws.png",
                                                width="30px",
                                                height="auto",
                                            ),
                                        ),
                                        (
                                            "gcp",
                                            rx.image(
                                                "/gcp.png",
                                                width="30px",
                                                height="auto",
                                            ),
                                        ),
                                        (
                                            "azure",
                                            rx.image(
                                                "/azr.png",
                                                width="35px",
                                                height="auto",
                                            ),
                                        ),
                                        (
                                            "vmw",
                                            rx.image(
                                                "/vmw.png",
                                                width="30px",
                                                height="auto",
                                            ),
                                        ),
                                    ),
                                    rx.text(x.region),
                                    class_name="text-lg p-2",
                                ),
                                rx.cond(
                                    State.current_cluster.status == "DELETED",
                                    rx.button(
                                        "DBConsole",
                                        disabled=True,
                                        class_name="p-2 mt-2 mx-12 cursor-pointer font-semibold text-lg",
                                    ),
                                    rx.button(
                                        "DBConsole",
                                        on_click=rx.redirect(
                                            f"https://{x.dns_address}:8080",
                                            is_external=True,
                                        ),
                                        class_name="p-2 mt-2 mx-12 cursor-pointer font-semibold text-lg",
                                    ),
                                ),
                                rx.cond(
                                    State.current_cluster.status == "DELETED",
                                    rx.button(
                                        "Connect",
                                        disabled=True,
                                        class_name="p-2 mt-2 mb-8 mx-12 cursor-pointer font-semibold text-lg",
                                    ),
                                    rx.popover.root(
                                        rx.popover.trigger(
                                            rx.button(
                                                "Connect",
                                                color_scheme="mint",
                                                class_name="p-2 mt-2 mb-8 mx-12 cursor-pointer font-semibold text-lg",
                                            ),
                                        ),
                                        rx.popover.content(
                                            rx.flex(
                                                rx.tooltip(
                                                    rx.code(
                                                        f"postgres://cockroach:cockroach@{x.dns_address}:26257/defaultdb?sslmode=require",
                                                        on_click=rx.set_clipboard(
                                                            f"postgres://cockroach:cockroach@{x.dns_address}:26257/defaultdb?sslmode=require"
                                                        ),
                                                        class_name="cursor-pointer hover:underline",
                                                    ),
                                                    content="Copy to Clipboard",
                                                ),
                                                rx.popover.close(
                                                    rx.button(
                                                        "Close",
                                                        color_scheme="mint",
                                                    ),
                                                ),
                                                direction="column",
                                                spacing="3",
                                            ),
                                        ),
                                    ),
                                ),
                                class_name="flex-col",
                            ),
                        ),
                        class_name="min-w-80 min-h-96 ml-4",
                    ),
                    rx.card(
                        rx.text("Details", class_name="text-2xl font-semibold"),
                        rx.divider(class_name="my-2"),
                        rx.flex(
                            rx.hstack(
                                rx.text("Node CPUs"),
                                rx.text(
                                    State.current_cluster_description.node_cpus,
                                    class_name="text-lg font-semibold",
                                ),
                                class_name="py-2",
                                align="center",
                            ),
                            rx.hstack(
                                rx.text("Disk Size GB"),
                                rx.text(
                                    State.current_cluster_description.disk_size,
                                    class_name="text-lg font-semibold",
                                ),
                                class_name="py-2",
                                align="center",
                            ),
                            rx.box(class_name="py-2"),
                            rx.hstack(
                                rx.text("Created By"),
                                rx.text(
                                    State.current_cluster.created_by,
                                    class_name="text-lg font-semibold",
                                ),
                                class_name="py-2",
                                align="center",
                            ),
                            rx.hstack(
                                rx.text("Created At"),
                                rx.text(
                                    rx.moment(
                                        State.current_cluster.created_at,
                                        format=TS_FORMAT,
                                        tz="UTC",
                                    ),
                                    class_name="text-lg font-semibold",
                                ),
                                class_name="py-2",
                                align="center",
                            ),
                            rx.box(class_name="py-2"),
                            rx.hstack(
                                rx.text("Last Updated By"),
                                rx.text(
                                    State.current_cluster.updated_by,
                                    class_name="text-lg font-semibold",
                                ),
                                class_name="py-2",
                                align="center",
                            ),
                            rx.hstack(
                                rx.text("Last Updated At"),
                                rx.text(
                                    rx.moment(
                                        State.current_cluster.updated_at,
                                        format=TS_FORMAT,
                                        tz="UTC",
                                    ),
                                    class_name="text-lg font-semibold",
                                ),
                                class_name="py-2",
                                align="center",
                            ),
                            class_name="flex-col",
                        ),
                        class_name="min-w-80 min-h-96 ml-4",
                    ),
                    rx.card(
                        rx.text("Actions", class_name="text-2xl font-semibold"),
                        rx.divider(class_name="my-2"),
                        rx.hstack(
                            # DELETE CLUSTER
                            rx.cond(
                                State.current_cluster.status == "DELETED",
                                rx.box(),
                                rx.cond(
                                    BaseState.is_admin_or_rw,
                                    rx.alert_dialog.root(
                                        rx.alert_dialog.trigger(
                                            rx.box(
                                                rx.tooltip(
                                                    rx.icon(
                                                        "trash-2",
                                                        color=None,
                                                        size=30,
                                                        class_name="cursor-pointer text-red-500 hover:text-red-300 mr-4",
                                                    ),
                                                    content="Delete the cluster",
                                                ),
                                            ),
                                        ),
                                        rx.alert_dialog.content(
                                            rx.alert_dialog.title(
                                                State.current_cluster.cluster_id
                                            ),
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
                                                        on_click=lambda: ClusterState.delete_cluster(
                                                            State.current_cluster.cluster_id,
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
                                            class_name="mr-4",
                                        ),
                                        content="You need to have admin or rw role to delete a cluster",
                                    ),
                                ),
                            ),
                            # SCALE CLUSTER
                            rx.cond(
                                State.current_cluster.status == "DELETED",
                                rx.box(),
                                rx.cond(
                                    BaseState.is_admin_or_rw,
                                    scale_cluster_dialog(),
                                    rx.tooltip(
                                        rx.icon(
                                            "expand",
                                            size=30,
                                            color="gray",
                                            class_name="mr-4",
                                        ),
                                        content="You need to have admin or rw role to scale a cluster",
                                    ),
                                ),
                            ),
                            # UPGRADE CLUSTER
                            rx.cond(
                                State.current_cluster.status == "DELETED",
                                rx.box(),
                                rx.cond(
                                    BaseState.is_admin_or_rw,
                                    rx.tooltip(
                                        rx.icon(
                                            "circle-fading-arrow-up",
                                            color=None,
                                            size=30,
                                            class_name="cursor-pointer text-green-500 hover:text-green-300 mr-4",
                                        ),
                                        content="Upgrade the cluster",
                                    ),
                                    rx.tooltip(
                                        rx.icon(
                                            "circle-fading-arrow-up",
                                            color="gray",
                                            size=30,
                                            class_name="mr-4",
                                        ),
                                        content="You need to have admin or rw role to upgrade a cluster",
                                    ),
                                ),
                            ),
                            # DEBUG CLUSTER
                            rx.cond(
                                State.current_cluster.status == "DELETED",
                                rx.box(),
                                rx.cond(
                                    BaseState.is_admin_or_rw,
                                    rx.tooltip(
                                        rx.icon(
                                            "bug-play",
                                            size=30,
                                            color=None,
                                            class_name="cursor-pointer text-blue-500 hover:text-blue-300 mr-4",
                                        ),
                                        content="Debug the cluster",
                                    ),
                                    rx.tooltip(
                                        rx.icon(
                                            "bug-play",
                                            color="gray",
                                            size=30,
                                            class_name="mr-4",
                                        ),
                                        content="You need to have admin or rw role to debug a cluster",
                                    ),
                                ),
                            ),
                            rx.tooltip(
                                rx.link(
                                    rx.icon(
                                        "clipboard-list",
                                        size=30,
                                        color=None,
                                        class_name="cursor-pointer text-fuchsia-500 hover:text-fuchsia-300 mr-4",
                                    ),
                                    href=f"/clusters/{State.cluster_id}/jobs",
                                ),
                                content="List Jobs",
                            ),
                            spacing="0",
                            class_name="",
                        ),
                        class_name="min-w-80 min-h-96 ml-4",
                    ),
                ),
                class_name="flex-1 flex-col overflow-hidden",
            ),
            class_name="flex-1 pt-8 overflow-hidden",
        ),
        class_name="flex-col flex-1 overflow-hidden",
        on_mount=rx.cond(
            BaseState.is_logged_in,
            State.fetch_cluster,
            BaseState.just_return,
        ),
    )
