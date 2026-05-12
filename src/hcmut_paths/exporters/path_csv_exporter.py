from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from hcmut_paths.domain.types import NodeId


def export_path_csv_files(
    output_folder: Path,
    graph: Any,
    directed_graph: Any,
    paths: list[list[NodeId]],
) -> None:
    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    for idx, path in enumerate(paths):
        _export_vertex_csv(
            output_folder / f"path_{idx+1}_vertices.csv",
            graph,
            path,
        )
        _export_edge_csv(
            output_folder / f"path_{idx+1}_edges.csv",
            graph,
            directed_graph,
            path,
        )


def _export_vertex_csv(
    output_path: Path,
    graph: Any,
    path: list[NodeId],
) -> None:
    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "vertex_order",
            "node_id",
            "latitude",
            "longitude",
        ])

        for order, node in enumerate(path):
            lat = graph.nodes[node]["y"]
            lon = graph.nodes[node]["x"]
            writer.writerow([
                order,
                node,
                lat,
                lon,
            ])


def _export_edge_csv(
    output_path: Path,
    graph: Any,
    directed_graph: Any,
    path: list[NodeId],
) -> None:
    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "from_node",
            "to_node",
            "from_lat",
            "from_lon",
            "to_lat",
            "to_lon",
            "edge_length_m",
        ])

        for u, v in zip(path[:-1], path[1:]):
            edge_data = directed_graph.get_edge_data(u, v)

            if edge_data is None:
                continue

            length = edge_data.get("length", 0)

            writer.writerow([
                u,
                v,
                graph.nodes[u]["y"],
                graph.nodes[u]["x"],
                graph.nodes[v]["y"],
                graph.nodes[v]["x"],
                length,
            ])

