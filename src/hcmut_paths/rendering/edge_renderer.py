from __future__ import annotations

from typing import Any

import folium

from hcmut_paths.graph.geometry import edge_coordinates


def render_subgraph_edges(
    map_obj: folium.Map,
    graph: Any,
    subgraph: Any,
    min_length_threshold_m: float,
) -> None:
    drawn_edges = set()

    for u, v, data in subgraph.edges(data=True):
        if (u, v) in drawn_edges:
            continue

        drawn_edges.add((u, v))
        length = float(data.get("length", 0))

        if length < min_length_threshold_m:
            continue

        coords = edge_coordinates(graph, u, v, data)
        folium.PolyLine(
            coords,
            color="gray",
            weight=2,
            opacity=0.5,
        ).add_to(map_obj)

        middle_index = len(coords) // 2
        mid_lat, mid_lon = coords[middle_index]

        folium.Marker(
            [mid_lat, mid_lon],
            icon=folium.DivIcon(
                html=f"""
            <div style="
                font-size:10px;
                color:black;
                background:white;
                padding:2px;
                border-radius:3px;
                white-space: nowrap;
            ">
                {length:.0f}m
            </div>
            """
            ),
        ).add_to(map_obj)

