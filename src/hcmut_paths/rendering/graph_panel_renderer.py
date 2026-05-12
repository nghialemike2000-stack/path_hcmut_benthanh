from __future__ import annotations

from typing import Any
import json

import folium

from hcmut_paths.domain.types import NodeId
from hcmut_paths.graph.geometry import edge_coordinates
from hcmut_paths.rendering.static_asset_injector import (
    render_script_asset,
    render_style_asset,
)
from hcmut_paths.rendering.template_renderer import render_template


def render_graph_info_panel(
    map_obj: folium.Map,
    map_name: str,
    graph: Any,
    subgraph: Any,
    selected_nodes_list: list[NodeId],
    node_to_index: dict[NodeId, int],
) -> None:
    vertex_rows: list[str] = []
    vertex_coords: dict[int, list[float]] = {}

    for idx, node in enumerate(selected_nodes_list):
        lat = graph.nodes[node]["y"]
        lon = graph.nodes[node]["x"]
        vertex_coords[idx] = [lat, lon]
        vertex_rows.append(
            f'<span class="graph-panel__vertex" data-vertex-id="{idx}">'
            f"{idx:03d}"
            f"</span> | "
            f"{lat:.8f} | "
            f"{lon:.8f}"
        )

    edge_rows: list[str] = []
    edge_coords_by_id: dict[int, list[list[float]]] = {}
    edge_id = 0

    for u, v, data in subgraph.edges(data=True):
        if (
            u not in node_to_index
            or v not in node_to_index
        ):
            continue

        u_idx = node_to_index[u]
        v_idx = node_to_index[v]
        length = float(data.get("length", 0))
        edge_coords_by_id[edge_id] = edge_coordinates(graph, u, v, data)
        edge_rows.append(
            f'<span class="graph-panel__edge" data-edge-id="{edge_id}">'
            f"{u_idx:03d} | {v_idx:03d}"
            f"</span> | "
            f"{length:.2f}"
        )
        edge_id += 1

    panel_html = render_template(
        "ui/templates/graph_panel.html",
        {
            "GRAPH_PANEL_CSS": render_style_asset("ui/assets/css/graph_panel.css"),
            "TOTAL_VERTICES": str(len(selected_nodes_list)),
            "TOTAL_EDGES": str(len(subgraph.edges)),
            "VERTEX_ROWS": "\n".join(vertex_rows),
            "EDGE_ROWS": "\n".join(edge_rows),
            "MAP_INTERACTIONS_JS": render_script_asset(
                "ui/assets/js/map_interactions.js",
                {
                    "__MAP_NAME__": map_name,
                    "__VERTEX_COORDS__": json.dumps(vertex_coords),
                    "__EDGE_COORDS__": json.dumps(edge_coords_by_id),
                },
            ),
            "GRAPH_PANEL_JS": render_script_asset("ui/assets/js/graph_panel.js"),
        },
    )

    map_obj.get_root().html.add_child(
        folium.Element(panel_html)
    )
