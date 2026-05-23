from __future__ import annotations

from itertools import islice
from typing import Any

import networkx as nx

from hcmut_paths.domain.types import NodeId
from hcmut_paths.algorithms.yen_algorithm import yen_k_shortest_paths


def find_k_shortest_paths(
    directed_graph: Any,
    origin: NodeId,
    destination: NodeId,
    k_paths: int,
    node_to_index: dict[NodeId, int],
) -> tuple[
    list[list[NodeId]],
    list[dict],
    float,
]:
    paths, explanation_data, execution_ms = yen_k_shortest_paths(
        directed_graph,
        origin,
        destination,
        k_paths,
    )

    return (
        list(islice(paths, k_paths)),
        explanation_data,
        execution_ms,
    )


def route_length(directed_graph: Any, route: list[NodeId]) -> float:
    total = 0.0

    for u, v in zip(route[:-1], route[1:]):
        total += directed_graph.edges[u, v]["length"]

    return total


def route_lengths(directed_graph: Any, paths: list[list[NodeId]]) -> list[float]:
    return [route_length(directed_graph, path) for path in paths]


def display_path(
    path: list[NodeId],
    node_to_index: dict[NodeId, int],
    graph=None,
    real_node_labels: dict[NodeId, int] | None = None,
) -> str:

    labels = []

    for idx, node in enumerate(path):

        if node == "HCMUT_GATE":

            # Look up the gate's own unique vertex index instead of its neighbor's
            gate_id = node_to_index.get(node)

            current_label = f"(HCMUT)({gate_id})" if gate_id is not None else "(HCMUT)"

        elif node == "BEN_THANH_GATE":

            # Look up the gate's own unique vertex index instead of its neighbor's
            gate_id = node_to_index.get(node)

            current_label = (
                f"(Ben Thanh)({gate_id})" if gate_id is not None else "(Ben Thanh)"
            )

        else:

            if node not in node_to_index:
                continue

            current_label = str(node_to_index[node])

        labels.append(current_label)

        if idx < len(path) - 1 and graph is not None:

            u = path[idx]
            v = path[idx + 1]

            if graph.has_edge(u, v):

                dist = graph[u][v]["length"] / 1000

                labels.append(f"-({dist:.3f} km)->")

    return " ".join(labels)
