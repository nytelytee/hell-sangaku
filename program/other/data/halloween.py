# pyright: strict
from __future__ import annotations

from typing import final

from hell_sangaku.base.index import Index
from hell_sangaku.drawing.colors import ColorRGB

from .weights import Weights

white = ColorRGB.from_hex('#FFFFFF')
orange = ColorRGB.from_hex('#F06E16')
purple = ColorRGB.from_hex('#6F046F')
light_purple = ColorRGB.mix(purple, 4, white, 1)
light_orange = ColorRGB.mix(orange, 4, white, 1)

@final
class HalloweenProfilePictureMainTriangleData(Weights):
    circle_color = white
    predefined_colors = {
        Index.root(): orange
    }

@final
class HalloweenProfilePictureMainTriangleSymbolData(Weights):
    circle_color = white
    predefined_colors = {
        Index.root(): light_orange
    }

@final
class HalloweenProfilePictureNegativeTriangleData(Weights):
    circle_color = white
    predefined_colors = {
        Index.root(): purple,
        Index.root().root_side_a().base(): purple,
        Index.root().root_side_b().base(): purple,
        Index.root().root_side_c().base(): purple,
        **{
            getattr(getattr(
                Index.root(), root_side
            )().base(), base_side)().normal_horizontal(): purple
            for root_side in ('root_side_a', 'root_side_b', 'root_side_c')
            for base_side in ('base_side_left', 'base_side_right')
        },
    }

@final
class HalloweenProfilePictureNegativeTriangleSymbolData(Weights):
    circle_color = white
    predefined_colors = {
        Index.root(): light_purple,
        Index.root().root_side_a().base(): light_purple,
        Index.root().root_side_b().base(): light_purple,
        Index.root().root_side_c().base(): light_purple,
        **{
            getattr(getattr(
                Index.root(), root_side
            )().base(), base_side)().normal_horizontal(): light_purple
            for root_side in ('root_side_a', 'root_side_b', 'root_side_c')
            for base_side in ('base_side_left', 'base_side_right')
        },
    }

