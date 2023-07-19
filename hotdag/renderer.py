import io
import json
from typing import Set

import networkx
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


class GMLRenderer(Renderer):
    """Render the selected graph as a GML Graph payload."""

    def __init__(self):
        super().__init__(content_type="application/gml")

    def render(
        self, manifest: Manifest, graph: Graph, selected_nodes: Set[UniqueId]
    ) -> str:
        """Render the selection as a JSON array of node UniqueIDs."""
        subgraph = graph.get_subset_graph(selected_nodes)
        output = io.BytesIO()
        networkx.write_gml(subgraph.graph, path=output)
        output.seek(0)
        return output.read().decode("ascii")


class SVGRenderer(Renderer):
    """Render the selection as an SVG of the subgraph."""

    def __init__(self):
        super().__init__(content_type="image/svg+xml")

        self.color_map = {
            "source": "#3B4F4C",
            "seed": "#69855B",
            "snapshot": "#97A37A",
            "model": "#6C3A2B",
            "metric": "#8B5320",
            "test": "#C4293E",
            "exposure": "#CEA248",
        }

    def render(
        self, manifest: Manifest, graph: Graph, selected_nodes: Set[UniqueId]
    ) -> str:
        import networkx as nx

        subgraph = graph.get_subset_graph(selected_nodes).graph
        dot_code = nx.nx_pydot.to_pydot(subgraph)
        dot_code.set_rankdir("LR")

        # Style the graphviz graph
        for node in dot_code.get_nodes():
            node.set_shape("box")
            node_name = node.get_name()
            resource_type = node_name.split(".")[0][1:]
            node.set_color(self.color_map.get(resource_type, "black"))
            node.set_fillcolor(self.color_map.get(resource_type, "black"))
            node.set_fontcolor("white")
            node.set_style("filled")
            node.set_fontname("Arial")

        return dot_code.create_svg().decode("utf-8")


renderers = {
    "json": JSONRenderer,
    "text": TextRenderer,
    "svg": SVGRenderer,
    "gml": GMLRenderer,
}
