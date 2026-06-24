from typing import cast, final, override

from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from hell_sangaku.base.shapes import Point, Triangle
from hell_sangaku.base.tree import (BaseTriangleNode, Data, NormalTriangleNode,
                                    RootTriangleNode)
from hell_sangaku.base.types import MPLColor
from hell_sangaku.drawing.basic_data import ColorData
from hell_sangaku.drawing.basic_drawers import (DefaultFilteringDrawer,
                                                MatplotlibDrawer)
from hell_sangaku.drawing.colors import Color

from .utility import offset_polygon

# TODO: optimize in a similar way to the symbol drawer
#       add to patch collection if possible, and ignore transparent
#       patches

@final
class OutlineDrawer(MatplotlibDrawer, DefaultFilteringDrawer):

    def __init__(
        self, figure: Figure, axes: Axes, /,
        *,
        outline_scale: float = 0.02,
        outline_color: MPLColor = 'black',
        negative_outline_color: MPLColor = 'none',
    ):
        super().__init__(figure, axes)
        self.outline_scale = outline_scale
        self.outline_color = outline_color
        self.negative_outline_color = negative_outline_color
    
    def get_real_outline_color(
        self, /, data: dict[str, Data], negative: bool
    ) -> MPLColor:
        outline_color = (self.outline_color
                         if not negative else
                         self.negative_outline_color)
        if not isinstance(outline_color, str):
            return outline_color
        if outline_color == 'data':
            key = (
                'outline_color'
                if not negative else
                'negative_outline_color'
            )
        elif outline_color.startswith('data[') and outline_color.endswith(']'):
            key = outline_color[5:-1]
        else:
            return outline_color
        return cast(ColorData[Color], data[key]).color.to_hex()

    def get_inner_triangle(self, triangle: Triangle, /) -> Triangle:
        DATA = self.axes.transData
        FIGURE = self.figure.dpi_scale_trans
        # matplotlib does not like it when you try to transform
        # non-floats (well actually it's numpy that does not like it,
        # but i have no idea how to tell matplotlib to tell numpy to
        # keep the dtype as object, and if that even makes sense).
        p = [
            p.transform(DATA, FIGURE)
            for p in (triangle.a, triangle.b, triangle.c)
        ]
        min_side_length = min(
            [p[0].dist(p[1]), p[1].dist(p[2]), p[0].dist(p[2])]
        )
        small_p = offset_polygon(p, -self.outline_scale*min_side_length)
        small_p_data = [p.transform(FIGURE, DATA) for p in small_p]
        return Triangle(*small_p_data)

    def get_outline_path(self, /, triangle: Triangle) -> Path:
        float_triangle = Triangle(
            *[Point(float(x), float(y))
              for x, y in triangle.coords.T]
        )
        inner_triangle = self.get_inner_triangle(float_triangle)
        path = Path(float_triangle.draw_coords.T, closed=True)
        inner_path = Path(inner_triangle.draw_coords.T[::-1], closed=True)
        return Path.make_compound_path(path, inner_path)

    def draw_outline(
        self, /,
        triangle: Triangle,
        data: dict[str, Data],
        negative: bool
    ) -> None:
        try:
            outline_path = self.get_outline_path(triangle)
        except ZeroDivisionError:
            return
        patch = PathPatch(
            outline_path, edgecolor='none',
            facecolor=self.get_real_outline_color(data, negative=negative)
        )
        _ = self.axes.add_patch(patch)
    
    @override
    def root_draw_triangle(
        self, node: RootTriangleNode, /
    ) -> None:
        self.draw_outline(node.untransformed.triangle, node.data, False)
    
    @override
    def base_draw_triangle(
        self, node: BaseTriangleNode, /
    ) -> None:
        self.draw_outline(node.untransformed.triangle, node.data, False)
    
    @override
    def normal_draw_positive_triangle(
        self, node: NormalTriangleNode, /
    ) -> None:
        self.draw_outline(node.untransformed.triangle, node.data, False)
    
    @override
    def normal_draw_negative_triangle(
        self, node: NormalTriangleNode, /
    ) -> None:
        self.draw_outline(node.untransformed.triangle, node.data, True)
