import reflex as rx
import asyncio


# from ..state import State
from ..template import template
from ..models import Cluster, ClusterOverview, MsgID
from ..cp import app
from .. import db


class State(rx.State):
    current_cluster: Cluster = None
    clusters: list[ClusterOverview] = []

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
                    rx.text("Cluster Name"),
                    rx.input(
                        placeholder="Name", name="cluster_id", default_value="fab"
                    ),
                    rx.text("CPU per node"),
                    rx.input(name="node_cpu", default_value="4"),
                    rx.text("Nodes per Region"),
                    rx.input(name="node_count", default_value="3"),
                    rx.text("Regions"),
                    rx.input(name="regions", default_value="us-east-1"),
                    rx.text("CockroachDB version"),
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
