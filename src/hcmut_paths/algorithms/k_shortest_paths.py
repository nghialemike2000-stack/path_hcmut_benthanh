from __future__ import annotations

from itertools import islice
from typing import Any

import networkx as nx

from hcmut_paths.domain.types import NodeId


def find_k_shortest_paths(
    directed_graph: Any,
    origin: NodeId,
    destination: NodeId,
    k_paths: int,
) -> list[list[NodeId]]:
    paths_iter = nx.shortest_simple_paths(
        directed_graph,
        origin,
        destination,
        weight="length",
    )
    return list(islice(paths_iter, k_paths))


def route_length(directed_graph: Any, route: list[NodeId]) -> float:
    total = 0.0

    for u, v in zip(route[:-1], route[1:]):
        total += directed_graph.edges[u, v]["length"]

    return total


def route_lengths(directed_graph: Any, paths: list[list[NodeId]]) -> list[float]:
    return [
        route_length(directed_graph, path)
        for path in paths
    ]
