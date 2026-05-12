from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from hcmut_paths.config.settings import AppSettings
from hcmut_paths.application.route_map_pipeline import RouteMapPipeline


def main() -> None:
    settings = AppSettings.default()
    pipeline = RouteMapPipeline(settings=settings)
    pipeline.run()


if __name__ == "__main__":
    main()
