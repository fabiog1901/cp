import reflex as rx
from fastapi import FastAPI

from .backend.main import get_nodes, pull_from_mq

# Create a FastAPI app
api_app = FastAPI(title="My API")


# Add routes to the FastAPI app
@api_app.get("/api/prom-targets")
async def get_targets():
    return get_nodes()


app = rx.App(
    theme=rx.theme(
        appearance="inherit",
        has_background=True,
        radius="large",
        accent_color="orange",
    ),
    api_transformer=api_app,
)


app.register_lifespan_task(pull_from_mq)
