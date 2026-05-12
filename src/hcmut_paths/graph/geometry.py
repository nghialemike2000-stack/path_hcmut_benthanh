from __future__ import annotations

from typing import Any

from hcmut_paths.domain.types import NodeId


def edge_coordinates(graph: Any, u: NodeId, v: NodeId, edge_data: dict[str, Any]) -> list[list[float]]:
    geometry = edge_data.get("geometry", None)

    if geometry is not None:
        return [
            [lat, lon]
            for lon, lat in geometry.coords
        ]

    return [
        [graph.nodes[u]["y"], graph.nodes[u]["x"]],
        [graph.nodes[v]["y"], graph.nodes[v]["x"]],
    ]


def route_segments(graph: Any, directed_graph: Any, path: list[NodeId]) -> list[tuple[float, float]]:
    segments: list[tuple[float, float]] = []

    for u, v in zip(path[:-1], path[1:]):
        edge_data = directed_graph.get_edge_data(u, v)

        if edge_data is None:
            continue

        geometry = edge_data.get("geometry", None)

        if geometry is not None:
            coords = [
                (lat, lon)
                for lon, lat in geometry.coords
            ]
        else:
            coords = [
                (
                    graph.nodes[u]["y"],
                    graph.nodes[u]["x"],
                ),
                (
                    graph.nodes[v]["y"],
                    graph.nodes[v]["x"],
                ),
            ]

        segments.extend(coords)

    return segments

