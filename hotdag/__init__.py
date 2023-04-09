# SPDX-FileCopyrightText: 2023-present Nicholas Yager <yager@nicholasyager.com>
#
# SPDX-License-Identifier: MIT

from typing import Optional, Set

from dbt.compilation import Compiler, Linker
from dbt.contracts.graph.manifest import Manifest
from dbt.graph import (
    Graph,
    NodeSelector,
    SelectionDifference,
    SelectionIntersection,
    SelectionSpec,
    SelectionUnion,
    UniqueId,
)
from dbt.graph.cli import parse_from_definition


class HotDAG:
    """Class for interacting with manifests and selecting nodes."""

    def __init__(self, manifest_loader, renderer):
        """Initialize a HotDAG."""

        self.manifest_loader = manifest_loader
        self.renderer = renderer

        self.manifest: Optional[Manifest] = None
        self.graph: Optional[Graph] = None

    def _load_graph(self):
        compiler = Compiler(config={})
        linker = Linker()
        compiler.link_graph(linker=linker, manifest=self.manifest)
        self.graph = Graph(linker.graph)

    def load_manifest(self, *args, **kwargs):
        """Load the manifest using the provided ManifestLoader."""

        self.manifest = self.manifest_loader.load(*args, **kwargs)
        self._load_graph()

    @staticmethod
    def string_to_definition(selection: str) -> SelectionSpec:
        """Parse CLI-provided selection strings into a SelectionSpec"""
        unions = selection.split(" ")
        union_components = []
        for union in unions:
            intersections = selection.split(",")
            if len(intersections) == 1:
                union_components.append(parse_from_definition(union))
            else:
                union_components.append(
                    SelectionIntersection(
                        components=[
                            parse_from_definition(intersection)
                            for intersection in intersections
                        ]
                    )
                )
        return SelectionUnion(union_components)

    def get_selection(
        self, select: Optional[str] = None, exclude: Optional[str] = None
    ) -> Set[UniqueId]:
        """Get a selection of nodes based on a selection spec"""

        if select is None:
            select = "+*+"

        # Generate selector from string
        selector_definition = self.string_to_definition(selection=select)

        complete_spec = None
        if exclude:
            exclusion_definition = self.string_to_definition(selection=exclude)
            complete_spec = SelectionDifference(
                [selector_definition, exclusion_definition]
            )

        # Generate subgraph
        node_selector = NodeSelector(graph=self.graph, manifest=self.manifest)

        direct_nodes, indirect_nodes = node_selector.select_nodes(
            complete_spec if complete_spec else selector_definition
        )

        return direct_nodes

    def render(self, selected_nodes: Set[UniqueId], **kwargs) -> str:
        """Render the selection using the provided Renderer."""
        return self.renderer.render(
            manifest=self.manifest,
            graph=self.graph,
            selected_nodes=selected_nodes,
            **kwargs,
        )
