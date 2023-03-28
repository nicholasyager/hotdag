from typing import Dict, Optional

from fastapi import APIRouter, Body
from starlette.responses import Response

from hotdag import HotDAG
from hotdag.manifest import DictManifestLoader
from hotdag.renderer import renderers
from hotdag.server.routers import OutputTypes

router = APIRouter(prefix="/manifest", tags=["URL Source"])


@router.post("/")
async def from_manifest(
    select: str = "+*+",
    exclude: Optional[str] = None,
    output: OutputTypes = "json",
    manifest: Dict = Body(...),
):
    renderer = renderers[output]()

    hotdag = HotDAG(manifest_loader=DictManifestLoader(), renderer=renderer)

    hotdag.load_manifest(dict=manifest)
    selected_nodes = hotdag.get_selection(select, exclude)
    output = hotdag.render(selected_nodes)

    return Response(output, headers={"Content-Type": renderer.content_type})
