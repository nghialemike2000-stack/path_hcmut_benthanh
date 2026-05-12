from __future__ import annotations

from hcmut_paths.domain.models import Coordinate

BACH_KHOA_GATES: dict[str, Coordinate] = {
    "gate_1": Coordinate(10.772085537574405, 106.65770218648836),
    "gate_2": Coordinate(10.772689726821197, 106.66066833396891),
    "gate_3": Coordinate(10.773539119525351, 106.6613593305036),
}

BEN_THANH_GATES: dict[str, Coordinate] = {
    "north": Coordinate(10.773162054715135, 106.69763552764178),
    "east": Coordinate(10.77279460684222, 106.69850445081336),
    "south": Coordinate(10.772030759155927, 106.69834289980986),
    "west": Coordinate(10.772210782443693, 106.69757864713894),
}

GATE_DISPLAY_NAMES: dict[str, str] = {
    "gate_1": "HCMUT Gate 1",
    "gate_2": "HCMUT Gate 2",
    "gate_3": "HCMUT Gate 3",
    "north": "Ben Thanh North Gate",
    "east": "Ben Thanh East Gate",
    "south": "Ben Thanh South Gate",
    "west": "Ben Thanh West Gate",
}


def initial_bbox_coordinates() -> tuple[Coordinate, Coordinate]:
    return (
        list(BACH_KHOA_GATES.values())[0],
        list(BEN_THANH_GATES.values())[0],
    )

