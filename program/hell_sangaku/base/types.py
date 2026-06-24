from __future__ import annotations

from enum import Enum, auto
from typing import Any

# from mpmath import mpf  # type: ignore[import-untyped]

class IndexPart(Enum):
    ROOT = auto()
    ROOT_SIDE_A = auto()
    ROOT_SIDE_B = auto()
    ROOT_SIDE_C = auto()
    BASE = auto()
    BASE_SIDE_LEFT = auto()
    BASE_SIDE_RIGHT = auto()
    NORMAL_HORIZONTAL = auto()
    NORMAL_VERTICAL = auto()


class RootSideType(Enum):
    A = auto()
    B = auto()
    C = auto()


class BaseSideType(Enum):
    LEFT = auto()
    RIGHT = auto()


class NormalTriangleType(Enum):
    HORIZONTAL = auto()
    VERTICAL = auto()


class AngleID(Enum):
    A = auto()
    B = auto()
    C = auto()

type MPLColor = (tuple[float, float, float, float] |
                 tuple[float, float, float] |
                 str |
                 tuple[tuple[float, float, float, float], float] |
                 tuple[tuple[float, float, float], float] |
                 tuple[str, float] |
                 None)

# I want to be able to use mpmath floats, but mpmath has no type stubs,
# so everywhere where any operation is done with mpfs, basedpyright
# will report an unknown type error, so I would essentially need to add
# casts *everywhere*; I simply made the type refer to Any to avoid
# doing this.
type RealNumber = Any  #float | mpf
