from __future__ import annotations

from random import uniform
from typing import Any, final

from hell_sangaku.base.types import MPLColor
from hell_sangaku.drawing.colors import ColorHPLuv

from .main_triangle_drawer import MainTriangleDrawer


@final
class RandomHPLuvColorDrawer(MainTriangleDrawer):

    def _generate_random_color(
        self, *_args: Any, **_kwargs: Any
    ) -> MPLColor:
        return ColorHPLuv(uniform(0, 360), 100, 85).to_hex()

    root_triangle_color = _generate_random_color
    root_segment_a_color = _generate_random_color
    root_segment_b_color = _generate_random_color
    root_segment_c_color = _generate_random_color
    base_triangle_color = _generate_random_color
    base_segment_color = _generate_random_color
    base_side_pseudo_sector_color = _generate_random_color
    normal_positive_triangle_color = _generate_random_color
    normal_negative_triangle_color = _generate_random_color
    normal_horizontal_pseudo_sector_color = _generate_random_color
    normal_vertical_pseudo_sector_color = _generate_random_color
