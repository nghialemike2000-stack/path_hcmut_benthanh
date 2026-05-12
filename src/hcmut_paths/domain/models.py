from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from hcmut_paths.domain.types import NodeId


@dataclass(frozen=True)
class Coordinate:
    lat: float
    lon: float

    @classmethod
    def from_tuple(cls, value: tuple[float, float]) -> "Coordinate":
        return cls(lat=value[0], lon=value[1])

    def as_tuple(self) -> tuple[float, float]:
        return (self.lat, self.lon)

    def as_folium_location(self) -> list[float]:
        return [self.lat, self.lon]


@dataclass(frozen=True)
class GateDistanceAttempt:
    start_gate: str
    end_gate: str
    distance_m: float | None = None
    skipped: bool = False


@dataclass(frozen=True)
class GateSelection:
    start_gate: str
    end_gate: str
    origin_node: NodeId
    destination_node: NodeId
    distance_m: float


@dataclass(frozen=True)
class GateConnectorResult:
    origin_gate_node: NodeId
    destination_gate_node: NodeId
    origin_connector_length_m: float
    destination_connector_length_m: float


@dataclass(frozen=True)
class PipelineResult:
    html_path: Path
    graph_txt_path: Path

