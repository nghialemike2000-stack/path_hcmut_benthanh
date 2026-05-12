from __future__ import annotations

import folium

from hcmut_paths.domain.models import Coordinate


def create_base_map(center: Coordinate) -> folium.Map:
    return folium.Map(
        location=center.as_folium_location(),
        zoom_start=15,
        tiles="OpenStreetMap",
    )

