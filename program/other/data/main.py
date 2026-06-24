# pyright: strict
from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar, final

from hell_sangaku.base.index import Index
from hell_sangaku.drawing.colors import ColorRGB

from .weights import Weights

white = ColorRGB.from_hex('#FFFFFF')

purple = ColorRGB.from_hex('#270627')
light_purple = ColorRGB.mix(purple, 4, white, 1)

#green = ColorRGB.from_hex('#04361D')
green = ColorRGB.from_hex('#004C29')
light_green = ColorRGB.mix(green, 4, white, 1)

@final
class MainProfilePictureMainTriangleData(Weights):
    circle_color: ClassVar[ColorRGB] = white
    predefined_colors: ClassVar[Mapping[Index, ColorRGB]] = {
        Index.root(): purple
    }

@final
class MainProfilePictureMainTriangleSymbolData(Weights):
    circle_color: ClassVar[ColorRGB] = white
    predefined_colors: ClassVar[Mapping[Index, ColorRGB]] = {
        Index.root(): light_purple
    }

@final
class MainProfilePictureNegativeTriangleData(Weights):
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
class MainProfilePictureNegativeTriangleSymbolData(Weights):
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
