import json
from typing import Set

from dbt.contracts.graph.manifest import Manifest
from dbt.graph import Graph, UniqueId


class Renderer:
    def __init__(self, content_type: str):
        self.content_type = content_type

    def render(self, manifest: Manifest, graph: Graph, selected_nodes: Set[UniqueId]):
        """Render the selection."""
        raise NotImplementedError


class JSONRenderer(Renderer):
    """Render the selection as a JSON payload."""

    def __init__(self):
        super().__init__(content_type="application/json")

    def render(self, manifest: Manifest, graph: Graph, selected_nodes: Set[UniqueId]):
        """Render the selection as a JSON array of node UniqueIDs."""
        return json.dumps(list(selected_nodes))


class TextRenderer(Renderer):
    """Render the selection as a Text payload."""

    def __init__(self):
        super().__init__(content_type="application/text")

    def render(
        self, manifest: Manifest, graph: Graph, selected_nodes: Set[UniqueId]
    ) -> str:
        """Render the selection as a JSON array of node UniqueIDs."""
        return "\n".join(selected_nodes)


class SVGRenderer(Renderer):
    """Render the selection as an SVG of the subgraph."""

    def __init__(self):
        super().__init__(content_type="image/svg+xml")

    def render(
        self, manifest: Manifest, graph: Graph, selected_nodes: Set[UniqueId]
    ) -> str:
        import networkx as nx

        subgraph = graph.get_subset_graph(selected_nodes).graph
        dot_code = nx.nx_pydot.to_pydot(subgraph)
        dot_code.set_rankdir("LR")
        return dot_code.create_svg().decode("utf-8")


renderers = {"json": JSONRenderer, "text": TextRenderer, "svg": SVGRenderer}
