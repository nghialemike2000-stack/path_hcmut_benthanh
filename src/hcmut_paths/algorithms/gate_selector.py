from __future__ import annotations

from typing import Any

import networkx as nx
import osmnx as ox

from hcmut_paths.domain.models import Coordinate, GateDistanceAttempt, GateSelection


def find_best_gate_pair(
    graph: Any,
    directed_graph: Any,
    start_gates: dict[str, Coordinate],
    end_gates: dict[str, Coordinate],
) -> tuple[GateSelection, list[GateDistanceAttempt]]:
    best_distance = float("inf")
    best_start_gate: str | None = None
    best_end_gate: str | None = None
    best_origin_node = None
    best_destination_node = None
    attempts: list[GateDistanceAttempt] = []

    for start_name, start_point in start_gates.items():
        for end_name, end_point in end_gates.items():
            try:
                temp_origin = ox.nearest_nodes(
                    graph,
                    X=start_point.lon,
                    Y=start_point.lat,
                )
                temp_destination = ox.nearest_nodes(
                    graph,
                    X=end_point.lon,
                    Y=end_point.lat,
                )
                temp_distance = nx.shortest_path_length(
                    directed_graph,
                    temp_origin,
                    temp_destination,
                    weight="length",
                )

                attempts.append(
                    GateDistanceAttempt(
                        start_gate=start_name,
                        end_gate=end_name,
                        distance_m=temp_distance,
                    )
                )

                if temp_distance < best_distance:
                    best_distance = temp_distance
                    best_start_gate = start_name
                    best_end_gate = end_name
                    best_origin_node = temp_origin
                    best_destination_node = temp_destination

            except Exception:
                attempts.append(
                    GateDistanceAttempt(
                        start_gate=start_name,
                        end_gate=end_name,
                        skipped=True,
                    )
                )

    if (
        best_start_gate is None
        or best_end_gate is None
        or best_origin_node is None
        or best_destination_node is None
    ):
        raise RuntimeError("No valid gate pair found")

    return (
        GateSelection(
            start_gate=best_start_gate,
            end_gate=best_end_gate,
            origin_node=best_origin_node,
            destination_node=best_destination_node,
            distance_m=best_distance,
        ),
        attempts,
    )

