from typing import ClassVar

from hell_sangaku.drawing.basic_data import ColorData
from hell_sangaku.drawing.colors import ColorRGB


class Weights(ColorData[ColorRGB]):
    base_parent_weight: ClassVar[float] = 8
    base_circle_weight: ClassVar[float] = 1
    horizontal_touching_vertical_weight: ClassVar[float] = 1
    horizontal_touching_horizontal_weight: ClassVar[float] = 8
    horizontal_circle_weight: ClassVar[float] = 1
    vertical_touching_vertical_weight: ClassVar[float] = 8
    vertical_touching_horizontal_weight: ClassVar[float] = 1
    vertical_circle_weight: ClassVar[float] = 1
