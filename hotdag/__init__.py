# SPDX-FileCopyrightText: 2023-present Nicholas Yager <yager@nicholasyager.com>
#
# SPDX-License-Identifier: MIT
from typing import Dict, List

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

    @property
    def depends_on_nodes(self):
        return self.depends_on.get('nodes', [])

    @property
    def empty(self):
        return not self.raw_code.strip()


class CompiledNode(SlimNode):
    resource_type: NodeType
    fqn: List[str]
