from __future__ import annotations

import folium

from hcmut_paths.domain.models import Coordinate


def render_main_location_markers(
    map_obj: folium.Map,
    ben_thanh_coordinate: Coordinate,
    bach_khoa_coordinate: Coordinate,
    end_gate: str,
    start_gate: str,
    gate_display_names: dict[str, str],
) -> None:
    folium.Marker(
        location=ben_thanh_coordinate.as_folium_location(),
        popup=f"Ben Thanh {gate_display_names[end_gate]}",
        icon=folium.Icon(color="red"),
    ).add_to(map_obj)

    folium.Marker(
        location=bach_khoa_coordinate.as_folium_location(),
        popup=f"HCMUT {gate_display_names[start_gate]}",
        icon=folium.Icon(color="blue"),
    ).add_to(map_obj)

