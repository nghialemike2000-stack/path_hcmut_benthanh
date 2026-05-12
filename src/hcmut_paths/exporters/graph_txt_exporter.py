from __future__ import annotations

from pathlib import Path
from typing import Any

from hcmut_paths.domain.types import NodeId


def export_graph_txt(
    output_path: Path,
    graph: Any,
    subgraph: Any,
    selected_nodes_list: list[NodeId],
    node_to_index: dict[NodeId, int],
) -> None:
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(f"VERTICES {len(selected_nodes_list)}\n\n")

        for idx, node in enumerate(selected_nodes_list):
            lat = graph.nodes[node]["y"]
            lon = graph.nodes[node]["x"]

            file.write(
                f"{idx} {lat:.8f} {lon:.8f}\n"
            )

        file.write("\nEDGES\n\n")

        written_edges = set()

        for u, v, data in subgraph.edges(data=True):
            edge_key = tuple(sorted((str(u), str(v))))

            if edge_key in written_edges:
                continue

            written_edges.add(edge_key)

            if (
                u not in node_to_index
                or v not in node_to_index
            ):
                continue

            u_idx = node_to_index[u]
            v_idx = node_to_index[v]
            length = float(
                data.get("length", 0)
            )

            file.write(
                f"{u_idx} "
                f"{v_idx} "
                f"{length:.2f}\n"
            )

