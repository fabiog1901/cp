"""Prometheus target API routes."""

from fastapi import APIRouter

from ..prometheus import get_nodes

router = APIRouter(tags=["prometheus"])


@router.get("/prom-targets")
async def get_targets():
    return get_nodes()
