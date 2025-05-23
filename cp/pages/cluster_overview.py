import asyncio

import reflex as rx

from .. import db
from ..components.BadgeClusterStatus import get_cluster_status_badge
from ..components.BadgeJobStatus import get_job_status_badge
from ..cp import app
from ..models import TS_FORMAT, Cluster, Job
from ..state.base import BaseState
from ..template import template
from .clusters import State as ClusterState


class State(BaseState):
    current_cluster: Cluster = None
    current_cluster_description: dict = {}
    current_cluster_regions: list[dict[str, str | list[str]]] = []
    current_cluster_lbs: list[dict[str, str]] = []

    @rx.var
    def cluster_id(self) -> str | None:
        return self.router.page.params.get("c_id") or None

    is_running: bool = False

    @rx.event(background=True)
    async def fetch_cluster(self):
        if self.is_running:
            return
        async with self:
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
            await asyncio.sleep(5)


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
