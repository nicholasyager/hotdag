from typing import Optional

from fastapi import APIRouter
from starlette.responses import Response

from hotdag import HotDAG
from hotdag.manifest import URLManifestLoader
from hotdag.renderer import JSONRenderer, SVGRenderer

router = APIRouter(prefix="/url", tags=["URL Source"])


@router.get("/")
async def from_url(
    url: str,
    select: str = "+*+",
    exclude: Optional[str] = None,
):
    hotdag = HotDAG(manifest_loader=URLManifestLoader(), renderer=JSONRenderer())

    hotdag.load_manifest(url=url)
    selected_nodes = hotdag.get_selection(select, exclude)
    return hotdag.render(selected_nodes)


@router.get("/svg")
async def svg_from_url(
    url: str,
    select: str = "+*+",
    exclude: Optional[str] = None,
):
    hotdag = HotDAG(manifest_loader=URLManifestLoader(), renderer=SVGRenderer())

    hotdag.load_manifest(url=url)
    selected_nodes = hotdag.get_selection(select, exclude)
    svg = hotdag.render(selected_nodes)

    return Response(svg, headers={"Content-Type": "image/svg+xml"})
