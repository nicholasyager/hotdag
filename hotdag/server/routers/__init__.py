from typing import Tuple, Set, Optional

import networkx as nx
from dbt.contracts.graph.manifest import Manifest
from dbt.graph import UniqueId, Graph, NodeSelector, SelectionDifference
from dbt.graph.cli import parse_from_definition
from loguru import logger


async def get_selected_nodes(
    graph: Graph, manifest: Manifest, select: str, exclude: Optional[str] = None
) -> Tuple[Set[UniqueId], Set[UniqueId]]:
    # Generate selector from string
    selector_definition = parse_from_definition(definition=select)

    exclusion_definition = None
    if exclude:
        exclusion_definition = parse_from_definition(definition=exclude)

    logger.info(selector_definition)

    # Generate subgraph
    node_selector = NodeSelector(graph=graph, manifest=manifest)

    return node_selector.select_nodes(
        SelectionDifference([selector_definition, exclusion_definition])
        if exclusion_definition
        else selector_definition
    )


async def generate_svg(direct_nodes, graph):
    subgraph = graph.get_subset_graph(direct_nodes).graph
    dot_code = nx.nx_pydot.to_pydot(subgraph)
    dot_code.set_rankdir("LR")
    svg = dot_code.create_svg().decode("utf-8")
    return svg
