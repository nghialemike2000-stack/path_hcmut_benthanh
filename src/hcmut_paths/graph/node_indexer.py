from __future__ import annotations

from hcmut_paths.domain.types import NodeId


def build_node_index(
    selected_nodes: set[NodeId],
) -> tuple[
    list[NodeId],
    dict[NodeId, int],
]:

    integer_nodes = sorted(
        [
            node
            for node in selected_nodes
            if isinstance(node, int)
        ]
    )

    special_nodes = [
        node
        for node in selected_nodes
        if isinstance(node, str)
    ]

    selected_nodes_list = (
        integer_nodes + special_nodes
    )

    node_to_index = {
        node: idx
        for idx, node in enumerate(
            selected_nodes_list
        )
    }

    return (
        selected_nodes_list,
        node_to_index,
    )