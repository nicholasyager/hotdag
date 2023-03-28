from typing import Dict, Optional

from fastapi import APIRouter, Body
from starlette.responses import Response

from hotdag import HotDAG
from hotdag.manifest import FileManifestLoader
from hotdag.renderer import JSONRenderer, SVGRenderer

router = APIRouter(prefix="/manifest", tags=["URL Source"])


@router.post("/")
async def from_manifest(
    select: str = "+*+", exclude: Optional[str] = None, manifest: Dict = Body(...)
):
    hotdag = HotDAG(manifest_loader=FileManifestLoader(), renderer=JSONRenderer())

    hotdag.load_manifest(dict=manifest)
    selected_nodes = hotdag.get_selection(select, exclude)
    return hotdag.render(selected_nodes)


@router.post("/svg")
async def svg_from_manifest(
    select: str = "+*+", exclude: Optional[str] = None, manifest: Dict = Body(...)
):
    hotdag = HotDAG(manifest_loader=FileManifestLoader(), renderer=SVGRenderer())

    hotdag.load_manifest(dict=manifest)
    selected_nodes = hotdag.get_selection(select, exclude)
    svg = hotdag.render(selected_nodes)

    return Response(svg, headers={"Content-Type": "image/svg+xml"})
