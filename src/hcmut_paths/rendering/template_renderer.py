from __future__ import annotations

from importlib import resources


def read_package_text(relative_path: str) -> str:
    return (
        resources.files("hcmut_paths")
        .joinpath(relative_path)
        .read_text(encoding="utf-8")
    )


def render_template(relative_path: str, context: dict[str, str]) -> str:
    content = read_package_text(relative_path)

    for key, value in context.items():
        content = content.replace("{{ " + key + " }}", value)

    return content

