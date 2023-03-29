from typing import Optional

from fastapi import APIRouter
from starlette.responses import Response

from hotdag import HotDAG
from hotdag.manifest import DBTCloudLoader
from hotdag.renderer import renderers
from hotdag.server.routers import OutputTypes

router = APIRouter(prefix="/cloud", tags=["URL Source"])


@router.get("/")
async def from_url(
    token: str,
    account_id: int,
    job_id: int,
    select: str = "+*+",
    exclude: Optional[str] = None,
    output: OutputTypes = "json",
):
    renderer = renderers[output]()

    hotdag = HotDAG(manifest_loader=DBTCloudLoader(api_key=token), renderer=renderer)

    hotdag.load_manifest(account_id=account_id, job_id=job_id)
    selected_nodes = hotdag.get_selection(select, exclude)
    output = hotdag.render(selected_nodes)

    return Response(output, headers={"Content-Type": renderer.content_type})
