from __future__ import annotations

from typing import Any

import folium
from folium import FeatureGroup

from hcmut_paths.domain.types import NodeId
from hcmut_paths.graph.geometry import route_segments
from hcmut_paths.rendering.template_renderer import render_template


def render_path_layers(
    map_obj: folium.Map,
    graph: Any,
    directed_graph: Any,
    paths: list[list[NodeId]],
    lengths: list[float],
    node_to_index: dict[NodeId, int],
    gate_display_names: dict[str, str],
    start_gate: str,
    end_gate: str,
    colors: list[str],
    base_weight: int,
) -> FeatureGroup:
    all_paths_group = FeatureGroup(
        name="Show All Paths",
        show=True,
    )

    for idx, path in enumerate(paths):
        color = colors[idx % len(colors)]
        line_weight = max(3, base_weight - idx)
        path_group = FeatureGroup(
            name=f"Path {idx+1} ({lengths[idx]/1000:.2f} km)",
            show=False,
        )

        segments = route_segments(graph, directed_graph, path)
        path_popup = render_template(
            "ui/templates/popup_path.html",
            {
                "PATH_NUMBER": str(idx + 1),
                "DISTANCE_KM": f"{lengths[idx]/1000:.2f}",
            },
        )

        folium.PolyLine(
            segments,
            color=color,
            weight=line_weight,
            opacity=0.9,
            popup=path_popup,
        ).add_to(path_group)

        folium.PolyLine(
            segments,
            color=color,
            weight=line_weight,
            opacity=0.9,
            popup=path_popup,
        ).add_to(all_paths_group)

        _render_path_nodes(
            path_group,
            graph,
            path,
            idx + 1,
            node_to_index,
        )
        _render_endpoint_markers(
            path_group,
            graph,
            path,
            idx + 1,
            node_to_index,
            gate_display_names,
            start_gate,
            end_gate,
        )

        path_group.add_to(map_obj)

    return all_paths_group


def _render_path_nodes(
    path_group: FeatureGroup,
    graph: Any,
    path: list[NodeId],
    path_number: int,
    node_to_index: dict[NodeId, int],
) -> None:
    for node in path:
        lat = graph.nodes[node]["y"]
        lon = graph.nodes[node]["x"]

        popup = render_template(
            "ui/templates/popup_path_node.html",
            {
                "VERTEX_ID": str(node_to_index[node]),
                "PATH_NUMBER": str(path_number),
                "LATITUDE": f"{lat:.8f}",
                "LONGITUDE": f"{lon:.8f}",
            },
        )

        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            weight=2,
            color="white",
            fill=True,
            fill_color="red",
            fill_opacity=1.0,
            popup=popup,
        ).add_to(path_group)


def _render_endpoint_markers(
    path_group: FeatureGroup,
    graph: Any,
    path: list[NodeId],
    path_number: int,
    node_to_index: dict[NodeId, int],
    gate_display_names: dict[str, str],
    start_gate: str,
    end_gate: str,
) -> None:
    first_node = path[0]
    last_node = path[-1]
    first_lat = graph.nodes[first_node]["y"]
    first_lon = graph.nodes[first_node]["x"]
    last_lat = graph.nodes[last_node]["y"]
    last_lon = graph.nodes[last_node]["x"]

    start_popup = render_template(
        "ui/templates/popup_endpoint.html",
        {
            "ENDPOINT_LABEL": "Start",
            "PATH_NUMBER": str(path_number),
            "PLACE_LABEL": "HCMUT",
            "GATE_DISPLAY_NAME": gate_display_names[start_gate],
            "VERTEX_ID": str(node_to_index[first_node]),
            "LATITUDE": f"{first_lat:.8f}",
            "LONGITUDE": f"{first_lon:.8f}",
        },
    )
    folium.Marker(
        location=[first_lat, first_lon],
        popup=start_popup,
        icon=folium.Icon(color="green"),
    ).add_to(path_group)

    end_popup = render_template(
        "ui/templates/popup_endpoint.html",
        {
            "ENDPOINT_LABEL": "End",
            "PATH_NUMBER": str(path_number),
            "PLACE_LABEL": "Ben Thanh",
            "GATE_DISPLAY_NAME": gate_display_names[end_gate],
            "VERTEX_ID": str(node_to_index[last_node]),
            "LATITUDE": f"{last_lat:.8f}",
            "LONGITUDE": f"{last_lon:.8f}",
        },
    )
    folium.Marker(
        location=[last_lat, last_lon],
        popup=end_popup,
        icon=folium.Icon(color="darkred"),
    ).add_to(path_group)

