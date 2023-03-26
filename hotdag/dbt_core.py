from typing import Dict

from dbt.compilation import Compiler, Linker
from dbt.contracts.graph.manifest import Manifest
from dbt.graph import Graph

from hotdag import CompiledNode, Node, SlimNode


async def compile_graph(manifest):
    """Compile the Manifest into a dbt Graph."""
    compiler = Compiler(config={})
    linker = Linker()
    compiler.link_graph(linker=linker, manifest=manifest)
    graph = Graph(linker.graph)
    return graph


def deserialize_manifest(manifest_dict: Dict) -> Manifest:
    return Manifest(
        nodes={
            unique_id: CompiledNode(**value)
            for unique_id, value in manifest_dict.get("nodes").items()
        },
        sources={
            unique_id: Node(**value)
            for unique_id, value in manifest_dict.get("sources").items()
        },
        macros={
            unique_id: SlimNode(**value)
            for unique_id, value in manifest_dict.get("macros").items()
        },
        docs={
            unique_id: Node(**value)
            for unique_id, value in manifest_dict.get("docs").items()
        },
        exposures={
            unique_id: SlimNode(**value)
            for unique_id, value in manifest_dict.get("exposures").items()
        },
        selectors={
            unique_id: value
            for unique_id, value in manifest_dict.get("selectors").items()
        },
    )
