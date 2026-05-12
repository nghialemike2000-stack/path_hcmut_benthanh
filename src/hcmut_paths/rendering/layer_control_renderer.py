from __future__ import annotations

import folium

from hcmut_paths.rendering.static_asset_injector import inject_header_style


def render_layer_control(map_obj: folium.Map) -> None:
    folium.LayerControl(
        position="bottomleft",
        collapsed=False,
    ).add_to(map_obj)


def inject_layer_control_styles(map_obj: folium.Map) -> None:
    inject_header_style(map_obj, "ui/assets/css/layer_control.css")

