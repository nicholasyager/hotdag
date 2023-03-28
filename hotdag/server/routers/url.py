from typing import Optional

from fastapi import APIRouter
from starlette.responses import Response

from hotdag.dbt_core import compile_graph
from hotdag.server.routers import get_selected_nodes, generate_svg
from hotdag.url_manifests import get_manifest_from_url

router = APIRouter(prefix="/url", tags=["URL Source"])


@router.get("/")
async def from_url(
        url: str,
        select: str = "+*+",
        exclude: Optional[str] = None,
):
    manifest = get_manifest_from_url(url)
    graph = await compile_graph(manifest)

    direct_nodes, indirect_nodes = await get_selected_nodes(
        graph=graph, manifest=manifest, select=select, exclude=exclude
    )

    return direct_nodes


@router.get("/svg")
async def svg_from_url(
        url: str,
        select: str = "+*+",
        exclude: Optional[str] = None,
):
    manifest = get_manifest_from_url(url)
    graph = await compile_graph(manifest)

    direct_nodes, indirect_nodes = await get_selected_nodes(
        graph=graph, manifest=manifest, select=select, exclude=exclude
    )

    svg = await generate_svg(direct_nodes, graph)

    return Response(svg, headers={"Content-Type": "image/svg+xml"})
