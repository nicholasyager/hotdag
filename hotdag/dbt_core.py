from typing import Dict, List

from dbt.contracts.graph.manifest import Manifest
from dbt.graph import UniqueId
from dbt.node_types import NodeType
from pydantic import BaseModel


class Config(BaseModel):
    enabled: bool = True


class Node(BaseModel):
    unique_id: UniqueId
    config: Config = Config()


class SlimNode(Node):
    depends_on: Dict[str, List[str]]
    raw_code: str = ""

    def __init__(self, *args, **data):
        if "raw_sql" in data:
            data["raw_code"] = data.get("raw_sql", data.get("raw_code"))

        super().__init__(*args, **data)

    @property
    def depends_on_nodes(self):
        return self.depends_on.get("nodes", [])

    @property
    def empty(self):
        return not self.raw_code.strip()


class CompiledNode(SlimNode):
    resource_type: NodeType
    fqn: List[str]


def compile_graph(manifest):
    """Compile the Manifest into a dbt Graph."""


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
