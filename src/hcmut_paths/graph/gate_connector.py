from __future__ import annotations

from typing import Any

import osmnx as ox
from geopy.distance import geodesic

from hcmut_paths.domain.models import Coordinate, GateConnectorResult
from hcmut_paths.domain.types import NodeId


def nearest_node(graph: Any, coordinate: Coordinate) -> NodeId:
    return ox.nearest_nodes(
        graph,
        X=coordinate.lon,
        Y=coordinate.lat,
    )


def connect_gate_nodes(
    graph: Any,
    origin_node: NodeId,
    destination_node: NodeId,
    origin_coordinate: Coordinate,
    destination_coordinate: Coordinate,
    origin_gate_node: NodeId,
    destination_gate_node: NodeId,
) -> GateConnectorResult:
    graph.add_node(
        origin_gate_node,
        y=origin_coordinate.lat,
        x=origin_coordinate.lon,
    )
    graph.add_node(
        destination_gate_node,
        y=destination_coordinate.lat,
        x=destination_coordinate.lon,
    )

    origin_node_coord = (
        graph.nodes[origin_node]["y"],
        graph.nodes[origin_node]["x"],
    )
    origin_connector_length = geodesic(
        origin_coordinate.as_tuple(),
        origin_node_coord,
    ).meters

    graph.add_edge(
        origin_gate_node,
        origin_node,
        length=origin_connector_length,
    )
    graph.add_edge(
        origin_node,
        origin_gate_node,
        length=origin_connector_length,
    )

    destination_node_coord = (
        graph.nodes[destination_node]["y"],
        graph.nodes[destination_node]["x"],
    )
    destination_connector_length = geodesic(
        destination_coordinate.as_tuple(),
        destination_node_coord,
    ).meters

    graph.add_edge(
        destination_node,
        destination_gate_node,
        length=destination_connector_length,
    )
    graph.add_edge(
        destination_gate_node,
        destination_node,
        length=destination_connector_length,
    )

    return GateConnectorResult(
        origin_gate_node=origin_gate_node,
        destination_gate_node=destination_gate_node,
        origin_connector_length_m=origin_connector_length,
        destination_connector_length_m=destination_connector_length,
    )

