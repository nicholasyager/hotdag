from typing import Dict, Optional, Set, Tuple

import networkx as nx
import requests
from dbt.contracts.graph.manifest import Manifest
from dbt.graph import Graph, NodeSelector, UniqueId
from dbt.graph.cli import parse_from_definition
from fastapi import Body, FastAPI
from loguru import logger
from starlette.responses import Response

from hotdag.dbt_core import compile_graph, deserialize_manifest

app = FastAPI()


async def get_selected_nodes(
    graph: Graph, manifest: Manifest, select: str, exclude: str
) -> Tuple[Set[UniqueId], Set[UniqueId]]:
    # Generate selector from string
    selector_definition = parse_from_definition(definition=select)

    logger.info(selector_definition)

    # Generate subgraph
    node_selector = NodeSelector(graph=graph, manifest=manifest)

    logger.info(node_selector)

    return node_selector.get_nodes_from_criteria(selector_definition)


async def generate_svg(direct_nodes, graph):
    subgraph = graph.get_subset_graph(direct_nodes).graph
    dot_code = nx.nx_pydot.to_pydot(subgraph)
    dot_code.set_rankdir("LR")
    svg = dot_code.create_svg().decode("utf-8")
    return svg


@app.get("/url")
async def from_url(
    url: str,
    select: str = "*",
    exclude: Optional[str] = None,
):
    logger.info("Getting manifest via URL.")
    response = requests.get(url, headers={"Content-Type": "application/json"})
    manifest = response.json()

    parsed_manifest = deserialize_manifest(manifest)
    graph = await compile_graph(parsed_manifest)

    direct_nodes, indirect_nodes = await get_selected_nodes(
        graph=graph, manifest=parsed_manifest, select=select, exclude=exclude
    )

    return direct_nodes


@app.get("/url/svg")
async def svg_from_url(
    url: str,
    select: str = "*",
    exclude: Optional[str] = None,
):
    logger.info("Getting manifest via URL.")
    response = requests.get(url, headers={"Content-Type": "application/json"})
    manifest = response.json()

    parsed_manifest = deserialize_manifest(manifest)
    graph = await compile_graph(parsed_manifest)

    direct_nodes, indirect_nodes = await get_selected_nodes(
        graph=graph, manifest=parsed_manifest, select=select, exclude=exclude
    )

    svg = await generate_svg(direct_nodes, graph)

    return Response(svg, headers={"Content-Type": "image/svg+xml"})


@app.post("/manifest")
async def from_manifest(
    select: str = "*", exclude: Optional[str] = None, manifest: Dict = Body(...)
):
    # Do some validation to make sure that the manifest payload is valid.

    parsed_manifest = deserialize_manifest(manifest)
    graph = await compile_graph(parsed_manifest)

    direct_nodes, indirect_nodes = await get_selected_nodes(
        graph=graph, manifest=parsed_manifest, select=select, exclude=exclude
    )

    return direct_nodes


@app.post("/manifest/svg")
async def svg_from_manifest(
    select: str = "*", exclude: Optional[str] = None, manifest: Dict = Body(...)
):
    parsed_manifest = deserialize_manifest(manifest)
    graph = await compile_graph(parsed_manifest)

    direct_nodes, indirect_nodes = await get_selected_nodes(
        graph=graph, manifest=parsed_manifest, select=select, exclude=exclude
    )

    svg = await generate_svg(direct_nodes, graph)

    return Response(svg, headers={"Content-Type": "image/svg+xml"})
