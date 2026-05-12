from __future__ import annotations

from typing import Any

import folium

from hcmut_paths.domain.types import NodeId
from hcmut_paths.rendering.template_renderer import render_template


def render_selected_vertices(
    map_obj: folium.Map,
    graph: Any,
    selected_nodes: set[NodeId],
    node_to_index: dict[NodeId, int],
) -> None:
    for node in selected_nodes:
        lat = graph.nodes[node]["y"]
        lon = graph.nodes[node]["x"]
        street_count = graph.nodes[node].get("street_count", 0)

        info_html = render_template(
            "ui/templates/popup_vertex.html",
            {
                "VERTEX_ID": str(node_to_index[node]),
                "LATITUDE": f"{lat:.8f}",
                "LONGITUDE": f"{lon:.8f}",
                "STREET_COUNT": str(street_count),
            },
        )

        vertex_marker = folium.CircleMarker(
            location=[lat, lon],
            radius=7,
            color="white",
            weight=2,
            fill=True,
            fill_color="green",
            fill_opacity=0.9,
            tooltip=folium.Tooltip(info_html, sticky=True),
        )
        folium.Popup(info_html).add_to(vertex_marker)
        vertex_marker.add_to(map_obj)

        marker_name = f"vertex_marker_{node_to_index[node]}"
        vertex_marker._name = marker_name

