from __future__ import annotations

from pathlib import Path

import folium


def export_html_map(map_obj: folium.Map, output_path: Path) -> None:
    map_obj.save(output_path)

