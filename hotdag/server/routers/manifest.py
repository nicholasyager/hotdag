from typing import Optional, Dict

from fastapi import APIRouter, Body
from starlette.responses import Response

from hotdag.dbt_core import compile_graph, deserialize_manifest
from hotdag.server.routers import get_selected_nodes, generate_svg

router = APIRouter(prefix="/manifest", tags=["URL Source"])


@router.post("/")
async def from_manifest(
    select: str = "+*+", exclude: Optional[str] = None, manifest: Dict = Body(...)
):
    # Do some validation to make sure that the manifest payload is valid.

    parsed_manifest = deserialize_manifest(manifest)
    graph = await compile_graph(parsed_manifest)

    direct_nodes, indirect_nodes = await get_selected_nodes(
        graph=graph, manifest=parsed_manifest, select=select, exclude=exclude
    )

    return direct_nodes


@router.post("/svg")
async def svg_from_manifest(
    select: str = "+*+", exclude: Optional[str] = None, manifest: Dict = Body(...)
):
    parsed_manifest = deserialize_manifest(manifest)
    graph = await compile_graph(parsed_manifest)

    direct_nodes, indirect_nodes = await get_selected_nodes(
        graph=graph, manifest=parsed_manifest, select=select, exclude=exclude
    )

    svg = await generate_svg(direct_nodes, graph)

    return Response(svg, headers={"Content-Type": "image/svg+xml"})
