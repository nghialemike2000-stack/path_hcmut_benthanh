from __future__ import annotations

from hcmut_paths.domain.types import NodeId


def build_node_index(
    selected_nodes: set[NodeId],
) -> tuple[list[NodeId], dict[NodeId, int]]:
    selected_nodes_list = list(selected_nodes)
    node_to_index: dict[NodeId, int] = {}

    for idx, node in enumerate(selected_nodes_list):
        node_to_index[node] = idx

    return selected_nodes_list, node_to_index

