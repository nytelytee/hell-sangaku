# pyright: strict
from __future__ import annotations

from typing import final

from hell_sangaku.base.index import Index
from hell_sangaku.drawing.colors import ColorRGB

from .weights import Weights

black = ColorRGB.from_hex('#000000')
white = ColorRGB.from_hex('#FFFFFF')
red = ColorRGB.from_hex('#97051D')
green = ColorRGB.from_hex('#04361D')

red = ColorRGB.from_hex('#900001')
green = ColorRGB.from_hex('#4D8200')
green = ColorRGB.from_hex('#335501')
green = ColorRGB.from_hex('#406B00')

light_red = ColorRGB.mix(red, 4, white, 1)
light_green = ColorRGB.mix(green, 4, white, 1)

@final
class ChristmasProfilePictureMainTriangleData(Weights):
    circle_color = white
    predefined_colors = {
        Index.root(): red
    }

@final
class ChristmasProfilePictureMainTriangleSymbolData(Weights):
    circle_color = white
    predefined_colors = {
        Index.root(): light_red
    }

@final
class ChristmasProfilePictureNegativeTriangleData(Weights):
    circle_color = white
    predefined_colors = {
        Index.root(): green,
        Index.root().root_side_a().base(): green,
        Index.root().root_side_b().base(): green,
        Index.root().root_side_c().base(): green,
        **{
            getattr(getattr(
                Index.root(), root_side
            )().base(), base_side)().normal_horizontal(): green
            for root_side in ('root_side_a', 'root_side_b', 'root_side_c')
            for base_side in ('base_side_left', 'base_side_right')
        },
    }

@final
class ChristmasProfilePictureNegativeTriangleSymbolData(Weights):
    circle_color = white
    predefined_colors = {
        Index.root(): light_green,
        Index.root().root_side_a().base(): light_green,
        Index.root().root_side_b().base(): light_green,
        Index.root().root_side_c().base(): light_green,
        **{
            getattr(getattr(
                Index.root(), root_side
            )().base(), base_side)().normal_horizontal(): light_green
            for root_side in ('root_side_a', 'root_side_b', 'root_side_c')
            for base_side in ('base_side_left', 'base_side_right')
        },
    }


