import asyncio

import reflex as rx

from .. import db
from ..components.BadgeClusterStatus import get_cluster_status_badge
from ..components.main import chip_props, item_selector
from ..cp import app
from ..models import (
    TS_FORMAT,
    Cluster,
    IntID,
    InventoryLB,
    InventoryRegion,
    Job,
    JobType,
    StrID,
)
from ..state.base import BaseState
from ..template import template
from ..util import get_human_size
from .clusters import State as ClusterState


class State(BaseState):
    current_cluster: Cluster | None = None

    auto_finalize: bool = True

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

        # TODO check if user is permissioned?
        msg_id: IntID = db.insert_into_mq(
            JobType.SCALE_CLUSTER,
            form_data,
            self.webuser.username,
        )
        db.insert_event_log(
            self.webuser.username,
            JobType.SCALE_CLUSTER,
            form_data | {"job_id": msg_id.id},
        )

        return rx.toast.info(f"Job {msg_id.id} requested.")

    @rx.event
    def upgrade_cluster(self, form_data: dict):
        form_data["name"] = self.current_cluster.cluster_id
        form_data["version"] = self.selected_version
        form_data["auto_finalize"] = self.auto_finalize

        msg_id: StrID = db.insert_into_mq(
            JobType.UPGRADE_CLUSTER,
            form_data,
            self.webuser.username,
        )
        db.insert_event_log(
            self.webuser.username,
            JobType.UPGRADE_CLUSTER,
            form_data | {"job_id": msg_id.id},
        )

        return rx.toast.info(f"Job {msg_id.id} requested.")

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

    @rx.var
    def is_major_upgrade_version(self) -> bool | None:
        if self.current_cluster:
            return self.current_cluster.version[:5] != self.selected_version[:5]
        return False

    @rx.var
    def human_disk_size(self) -> str | None:
        if self.current_cluster:
            return get_human_size(self.current_cluster.disk_size)
        return None

    is_running: bool = False
    just_once: bool = True

    @rx.event
    def reload_cluster_data(self):
        self.selected_node_count = self.current_cluster.node_count
        self.selected_cpus_per_node = self.current_cluster.node_cpus
        self.selected_disk_size = get_human_size(self.current_cluster.disk_size)
        self.selected_regions = [
            x.cloud + ":" + x.region for x in self.current_cluster.cluster_inventory
        ]

    @rx.event(background=True)
    async def fetch_cluster(self):
        if self.is_running:
            return
        async with self:
            # fetch this data only once

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
                    self.just_once = True
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

                self.current_cluster = cluster

                if self.just_once and self.current_cluster:
                    self.just_once = False

                    all_new_versions = [
                        x.id
                        for x in db.get_upgrade_versions(
                            self.current_cluster.version[:5]
                        )
                    ]

                    major_yy, major_mm, _ = [
                        int(x) for x in self.current_cluster.version[1:].split(".")
                    ]

                    self.available_versions = []
                    for v in all_new_versions:
                        f1, f2, _ = [int(x) for x in v[1:].split(".")]

                        # only a patch upgrade
                        if major_yy == f1 and major_mm == f2:
                            self.available_versions.append(v)
                            continue

                        # innovation to regular
                        if major_yy == f1 and major_mm in [1, 3] and f2 == major_mm + 1:
                            self.available_versions.append(v)
                            continue

                        if major_yy == f1 and major_mm == 2 and f2 in [3, 4]:
                            self.available_versions.append(v)
                            continue

                        if major_yy + 1 == f1 and major_mm == 4 and f2 in [1, 2]:
                            self.available_versions.append(v)

                    self.selected_version = (
                        self.available_versions[0] if self.available_versions else ""
                    )

                    self.selected_node_count = self.current_cluster.node_count

                    self.selected_cpus_per_node = self.current_cluster.node_cpus

                    self.selected_disk_size = get_human_size(
                        self.current_cluster.disk_size
                    )

                    self.selected_regions = [
                        x.cloud + ":" + x.region
                        for x in self.current_cluster.cluster_inventory
                    ]

            await asyncio.sleep(5)


chip_props = {
    "radius": "full",
    "variant": "surface",
    "size": "3",
    "cursor": "pointer",
    "style": {"_hover": {"opacity": 0.75}},
}


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
                lambda item: rx.badge(
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
                ),
            ),
            wrap="wrap",
            spacing="2",
            justify_content="start",
        ),
        rx.divider(),
        # Unselected Items
        rx.flex(
            rx.foreach(
                State.available_regions,
                lambda item: rx.cond(
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
                ),
            ),
            wrap="wrap",
            spacing="2",
            justify_content="start",
        ),
        justify_content="start",
        align_items="start",
        width="100%",
    )


def upgrade_cluster_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.box(
                rx.tooltip(
                    rx.icon(
                        "circle-fading-arrow-up",
                        color=None,
                        size=30,
                        class_name="cursor-pointer text-green-500 hover:text-green-300 mr-4",
                    ),
                    content="Upgrade the cluster",
                ),
            ),
        ),
        rx.dialog.content(
            rx.dialog.title(f"Upgrade {State.cluster_id}", class_name="text-4xl pb-4"),
            rx.form(
                rx.flex(
                    rx.vstack(
                        rx.heading("Select version to upgrade to", size="4"),
                        rx.select(
                            State.available_versions,
                            value=State.selected_version,
                            on_change=State.set_selected_version,
                            color_scheme="mint",
                            required=True,
                            class_name="min-w-64",
                        ),
                        class_name="min-w-64",
                    ),
                    rx.divider(),
                    rx.cond(
                        State.is_major_upgrade_version,
                        rx.vstack(
                            rx.hstack(
                                rx.heading("Auto finalize upgrade", size="4"),
                                rx.checkbox(
                                    checked=State.auto_finalize,
                                    on_change=State.set_auto_finalize,
                                ),
                                class_name="min-w-64",
                            ),
                            rx.divider(),
                        ),
                        rx.box(),
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
                            rx.button("Upgrade", type="submit"),
                        ),
                        spacing="3",
                        justify="end",
                    ),
                    direction="column",
                    spacing="4",
                ),
                on_submit=lambda form_data: State.upgrade_cluster(
                    form_data, BaseState.webuser
                ),
                reset_on_submit=False,
            ),
            max_width="850px",
        ),
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
            on_open_auto_focus=State.reload_cluster_data,
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
                        State.current_cluster.version,
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
                    # CLUSTER CARD
                    rx.card(
                        rx.text("Cluster", class_name="text-2xl font-semibold"),
                        rx.divider(class_name="my-2"),
                        rx.foreach(
                            State.current_cluster.cluster_inventory,
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
                    # LB CARD
                    rx.card(
                        rx.text("Load Balancers", class_name="text-2xl font-semibold"),
                        rx.divider(class_name="my-2"),
                        rx.foreach(
                            State.current_cluster.lbs_inventory,
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
                                    State.current_cluster.status.startswith("DELET"),
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
                                    State.current_cluster.status.startswith("DELET"),
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
                    # DETAIL CARD
                    rx.card(
                        rx.text("Details", class_name="text-2xl font-semibold"),
                        rx.divider(class_name="my-2"),
                        rx.flex(
                            rx.hstack(
                                rx.text("Number of Regions"),
                                rx.text(
                                    State.current_cluster.lbs_inventory.length(),
                                    class_name="text-lg font-semibold",
                                ),
                                class_name="py-2",
                                align="center",
                            ),
                            rx.hstack(
                                rx.text("Node Count per Region"),
                                rx.text(
                                    State.current_cluster.node_count,
                                    class_name="text-lg font-semibold",
                                ),
                                class_name="py-2",
                                align="center",
                            ),
                            rx.hstack(
                                rx.text("Node CPUs"),
                                rx.text(
                                    State.current_cluster.node_cpus,
                                    class_name="text-lg font-semibold",
                                ),
                                class_name="py-2",
                                align="center",
                            ),
                            rx.hstack(
                                rx.text("Disk Size"),
                                rx.text(
                                    State.human_disk_size,
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
                            rx.hstack(
                                rx.text("( about"),
                                rx.moment(
                                    State.current_cluster.created_at, from_now=True
                                ),
                                rx.text(")"),
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
                            rx.hstack(
                                rx.text("( about"),
                                rx.moment(
                                    State.current_cluster.updated_at, from_now=True
                                ),
                                rx.text(")"),
                            ),
                            class_name="flex-col",
                        ),
                        class_name="min-w-80 min-h-96 ml-4",
                    ),
                    # ACTIONS CARD
                    rx.card(
                        rx.text("Actions", class_name="text-2xl font-semibold"),
                        rx.divider(class_name="my-2"),
                        rx.hstack(
                            # DELETE CLUSTER
                            rx.cond(
                                State.current_cluster.status.startswith("DELET"),
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
                                State.current_cluster.status.startswith("DELET"),
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
                                State.current_cluster.status.startswith("DELET"),
                                rx.box(),
                                rx.cond(
                                    BaseState.is_admin_or_rw,
                                    upgrade_cluster_dialog(),
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
                                State.current_cluster.status.startswith("DELET"),
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
                            rx.cond(
                                State.current_cluster.status.startswith("DELET"),
                                rx.box(),
                                rx.cond(
                                    BaseState.is_admin_or_rw,
                                    rx.tooltip(
                                        rx.link(
                                            rx.icon(
                                                "database-backup",
                                                size=30,
                                                color=None,
                                                class_name="cursor-pointer text-green-500 hover:text-green-300 mr-4",
                                            ),
                                            href=f"/clusters/{State.cluster_id}/backups",
                                        ),
                                        content="List Backups",
                                    ),
                                    rx.tooltip(
                                        rx.icon(
                                            "database-backup",
                                            color="gray",
                                            size=30,
                                            class_name="mr-4",
                                        ),
                                        content="You need to have admin or rw role",
                                    ),
                                ),
                            ),
                            rx.cond(
                                State.current_cluster.status.startswith("DELET"),
                                rx.box(),
                                rx.cond(
                                    BaseState.is_admin_or_rw,
                                    rx.tooltip(
                                        rx.link(
                                            rx.icon(
                                                "users",
                                                size=30,
                                                color=None,
                                                class_name="cursor-pointer text-gray-500 hover:text-gray-300 mr-4",
                                            ),
                                            href=f"/clusters/{State.cluster_id}/users",
                                        ),
                                        content="List Users",
                                    ),
                                    rx.tooltip(
                                        rx.icon(
                                            "users",
                                            color="gray",
                                            size=30,
                                            class_name="mr-4",
                                        ),
                                        content="You need to have admin or rw role",
                                    ),
                                ),
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
