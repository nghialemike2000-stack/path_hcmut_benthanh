from __future__ import annotations

import csv
from pathlib import Path


def export_graph_csv(
    graph_txt_path: Path,
    output_folder: Path,
) -> None:

    output_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        graph_txt_path,
        "r",
        encoding="utf-8",
    ) as file:

        lines = [
            line.strip()
            for line in file.readlines()
            if line.strip()
        ]

    vertices = []
    edges = []

    reading_vertices = False
    reading_edges = False

    for line in lines:

        if line.startswith("VERTICES"):
            reading_vertices = True
            reading_edges = False
            continue

        if line.startswith("EDGES"):
            reading_vertices = False
            reading_edges = True
            continue

        if reading_vertices:

            parts = line.split()

            vertex_id = int(parts[0])
            lat = float(parts[1])
            lon = float(parts[2])

            vertices.append(
                (
                    vertex_id,
                    lat,
                    lon,
                )
            )

        elif reading_edges:

            parts = line.split()

            u = int(parts[0])
            v = int(parts[1])
            weight = float(parts[2])

            edges.append(
                (
                    u,
                    v,
                    weight,
                )
            )

    export_vertices_csv(
        output_folder / "vertices.csv",
        vertices,
    )

    export_adjacency_matrix_csv(
        output_folder / "adjacency_matrix.csv",
        vertices,
        edges,
    )


def export_vertices_csv(
    output_path: Path,
    vertices: list[tuple[int, float, float]],
) -> None:

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow(
            [
                "vertex_id",
                "latitude",
                "longitude",
            ]
        )

        for vertex_id, lat, lon in vertices:

            writer.writerow(
                [
                    vertex_id,
                    lat,
                    lon,
                ]
            )


def export_adjacency_matrix_csv(
    output_path: Path,
    vertices: list[tuple[int, float, float]],
    edges: list[tuple[int, int, float]],
) -> None:

    total_vertices = len(vertices)

    matrix = [
        ["inf"] * total_vertices
        for _ in range(total_vertices)
    ]

    for i in range(total_vertices):
        matrix[i][i] = 0

    for u, v, weight in edges:

        matrix[u][v] = round(weight, 2)
        matrix[v][u] = round(weight, 2)

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        header = ["vertex"] + list(
            range(total_vertices)
        )

        writer.writerow(header)

        for i in range(total_vertices):

            writer.writerow(
                [i] + matrix[i]
            )