from __future__ import annotations

from typing import Any

import osmnx as ox

from hcmut_paths.domain.models import Coordinate


def build_bbox(
    start: Coordinate,
    end: Coordinate,
    lat_padding: float,
    lon_padding: float,
) -> tuple[float, float, float, float]:
    north = max(end.lat, start.lat) + lat_padding
    south = min(end.lat, start.lat) - lat_padding
    east = max(end.lon, start.lon) + lon_padding
    west = min(end.lon, start.lon) - lon_padding
    return (west, south, east, north)


def load_consolidated_graph(
    bbox: tuple[float, float, float, float],
    custom_filter: str,
    intersection_tolerance_m: float,
) -> Any:
    raw_graph = ox.graph_from_bbox(
        bbox,
        custom_filter=custom_filter,
        simplify=True,
    )
    projected_graph = ox.project_graph(raw_graph)
    consolidated_graph = ox.consolidate_intersections(
        projected_graph,
        rebuild_graph=True,
        tolerance=intersection_tolerance_m,
        dead_ends=False,
    )
    return ox.project_graph(consolidated_graph, to_crs="EPSG:4326")

