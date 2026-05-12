from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    k_paths: int = 30
    target_vertices: int = 100
    min_length_threshold_m: float = 0
    network_type: str = "drive"
    lat_padding: float = 0.006
    lon_padding: float = 0.006
    intersection_tolerance_m: float = 25
    min_node_gap_m: float = 80
    output_html: Path = Path("hcmut_ben_thanh_k_paths.html")
    csv_output_folder: Path = Path("list_vertex")
    graph_txt_path: Path = Path("graph.txt")
    origin_gate_node: str = "HCMUT_GATE"
    destination_gate_node: str = "BEN_THANH_GATE"
    custom_filter: str = """
["highway"~"motorway|trunk|primary|secondary|tertiary"]
"""
    path_colors: list[str] = field(default_factory=lambda: [
        "#ff0000",
        "#0066ff",
        "#8a2be2",
        "#ff8800",
        "#00aa00",
        "#ff1493",
        "#00cccc",
        "#222222",
        "#999900",
        "#663300",
    ])
    base_path_weight: int = 8

    @classmethod
    def default(cls) -> "AppSettings":
        return cls()

