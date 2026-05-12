from __future__ import annotations

from typing import Any

import osmnx as ox


def to_weighted_digraph(graph: Any) -> Any:
    return ox.convert.to_digraph(graph, weight="length")

