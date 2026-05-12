from __future__ import annotations

import folium

from hcmut_paths.rendering.template_renderer import read_package_text


def render_style_asset(relative_path: str) -> str:
    css = read_package_text(relative_path)
    return f"<style>\n{css}\n</style>"


def render_script_asset(relative_path: str, replacements: dict[str, str] | None = None) -> str:
    javascript = read_package_text(relative_path)

    for key, value in (replacements or {}).items():
        javascript = javascript.replace(key, value)

    return f"<script>\n{javascript}\n</script>"


def inject_header_style(map_obj: folium.Map, relative_path: str) -> None:
    map_obj.get_root().header.add_child(
        folium.Element(render_style_asset(relative_path))
    )

