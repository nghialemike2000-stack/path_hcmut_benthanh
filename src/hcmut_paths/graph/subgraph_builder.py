from __future__ import annotations

from typing import Any

from geopy.distance import geodesic

from hcmut_paths.domain.models import Coordinate
from hcmut_paths.domain.types import NodeId


def collect_route_nodes(paths: list[list[NodeId]]) -> set[NodeId]:
    selected_nodes: set[NodeId] = set()
    for path in paths:
        for node in path:
            selected_nodes.add(node)
    return selected_nodes


def add_nearby_intersections(
    graph: Any,
    selected_nodes: set[NodeId],
    start_coordinate: Coordinate,
    end_coordinate: Coordinate,
    target_vertices: int,
    min_node_gap_m: float,
) -> set[NodeId]:
    center_lat = (end_coordinate.lat + start_coordinate.lat) / 2
    center_lon = (end_coordinate.lon + start_coordinate.lon) / 2

    def corridor_distance(node_id: NodeId) -> float:
        lat = graph.nodes[node_id]["y"]
        lon = graph.nodes[node_id]["x"]
        return geodesic(
            (lat, lon),
            (center_lat, center_lon),
        ).meters

    candidates: list[NodeId] = []
    for node, data in graph.nodes(data=True):
        if node in selected_nodes:
            continue

        street_count = int(data.get("street_count", 0))
        if street_count >= 3:
            candidates.append(node)

    candidates.sort(key=corridor_distance)

    for node in candidates:
        if len(selected_nodes) >= target_vertices:
            break

        node_lat = graph.nodes[node]["y"]
        node_lon = graph.nodes[node]["x"]

        is_too_close = False
        for selected_node in selected_nodes:
            selected_lat = graph.nodes[selected_node]["y"]
            selected_lon = graph.nodes[selected_node]["x"]

            dist = geodesic(
                (node_lat, node_lon),
                (selected_lat, selected_lon),
            ).meters

            if dist < min_node_gap_m:
                is_too_close = True
                break

        if not is_too_close:
            selected_nodes.add(node)

    return selected_nodes


def build_subgraph(graph: Any, selected_nodes: set[NodeId]) -> Any:
    return graph.subgraph(selected_nodes).copy()

