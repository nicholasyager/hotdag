from typing import Optional

from fastapi import APIRouter
from starlette.responses import Response

from hotdag import HotDAG
from hotdag.manifest import URLManifestLoader
from hotdag.renderer import renderers
from hotdag.server.routers import OutputTypes

router = APIRouter(prefix="/url", tags=["URL Source"])


@router.get("/")
async def from_url(
    url: str,
    select: str = "+*+",
    exclude: Optional[str] = None,
    output: OutputTypes = "json",
):
    renderer = renderers[output]()

    hotdag = HotDAG(manifest_loader=URLManifestLoader(), renderer=renderer)

    hotdag.load_manifest(url=url)
    selected_nodes = hotdag.get_selection(select, exclude)
    output = hotdag.render(selected_nodes)

    return Response(output, headers={"Content-Type": renderer.content_type})
