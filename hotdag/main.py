from typing import Dict, Optional

from dbt.compilation import Compiler, Linker
from dbt.contracts.graph.manifest import Manifest
from dbt.graph import NodeSelector, Graph
from dbt.graph.cli import parse_from_definition
from fastapi import FastAPI, Body
from loguru import logger

from hotdag import CompiledNode, Node, SlimNode

app = FastAPI()



@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.post("/manifest")
async def from_manifest(
        select: str = '*',
        exclude: Optional[str] = None,
        manifest: Dict = Body(...)
):
    logger.info(select)

    # Do some validation to make sure that the manifest payload is valid.

    # Serialize Manifest
    internal_manifest = Manifest(
        nodes={
            unique_id: CompiledNode(**value)
            for unique_id, value in manifest.get('nodes').items()
        },
        sources={
            unique_id: Node(**value)
            for unique_id, value in manifest.get('sources').items()
        },
        macros={
            unique_id: SlimNode(**value)
            for unique_id, value in manifest.get('macros').items()
        },
        docs={
            unique_id: Node(**value)
            for unique_id, value in manifest.get('docs').items()
        },
        exposures={
            unique_id: SlimNode(**value)
            for unique_id, value in manifest.get('exposures').items()
        },
        selectors={
            unique_id: value
            for unique_id, value in manifest.get('selectors').items()
        },
    )

    # internal_manifest.build_flat_graph()
    compiler = Compiler(config={})
    linker = Linker()
    compiler.link_graph(
        linker=linker,
        manifest=internal_manifest
    )
    graph = Graph(linker.graph)

    # Generate selector from string
    selector_definition = parse_from_definition(
        definition=select
    )

    # Generate subgraph
    node_selector = NodeSelector(
        graph=graph,
        manifest=internal_manifest
    )
    direct_nodes, indirect_nodes = node_selector.get_nodes_from_criteria(selector_definition)
    return direct_nodes

    # Generate graphviz

    # Return SVG

    return {"message": "Hello World"}
