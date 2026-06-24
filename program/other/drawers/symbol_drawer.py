from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast, final, override

import mpmath as mp  # pyright: ignore[reportMissingTypeStubs]
import numpy as np
import shapely
import shapely.geometry
from matplotlib.collections import PatchCollection
from matplotlib.patches import PathPatch
from matplotlib.path import Path

from hell_sangaku.base.shapes import Point, Triangle
from hell_sangaku.base.tree import (BaseTriangleNode, Data, NormalTriangleNode,
                                    RootTriangleNode, TriangleTree)
from hell_sangaku.base.types import MPLColor, RealNumber
from hell_sangaku.drawing.basic_data import ColorData
from hell_sangaku.drawing.basic_drawers import (DefaultFilteringDrawer,
                                                MatplotlibDrawer)
from hell_sangaku.drawing.colors import Color

from .utility import is_mpl_color_transparent

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


@final
class SymbolDrawer(MatplotlibDrawer, DefaultFilteringDrawer):

    symbol_edgecolor: MPLColor
    symbol_facecolor: MPLColor
    negative_symbol_edgecolor: MPLColor
    negative_symbol_facecolor: MPLColor
    linewidth_scale: RealNumber
    symbol_part_distance_scale: RealNumber
    symbol_outline_gap_scale: RealNumber
    inradius_scale: RealNumber
    quad_segs: int

    _symbol_paths: list[Path]
    _symbol_edgecolors: list[MPLColor]
    _symbol_facecolors: list[MPLColor]
    _symbol_linewidths: list[float]

    def __init__(
        self, /,
        figure: Figure, axes: Axes,
        symbol_edgecolor: MPLColor = 'black',
        symbol_facecolor: MPLColor = 'none',
        negative_symbol_edgecolor: MPLColor = 'black',
        negative_symbol_facecolor: MPLColor = 'none',
        linewidth_scale: RealNumber = 0.015,
        symbol_part_distance_scale: RealNumber = 0.2,
        symbol_outline_gap_scale: RealNumber = 0.2,
        inradius_scale: RealNumber = 0.8,
        quad_segs: int = 64
    ):
        super().__init__(figure, axes)
        self.symbol_edgecolor = symbol_edgecolor
        self.symbol_facecolor = symbol_facecolor
        self.negative_symbol_edgecolor = negative_symbol_edgecolor
        self.negative_symbol_facecolor = negative_symbol_facecolor
        self.linewidth_scale = linewidth_scale
        self.symbol_part_distance_scale = symbol_part_distance_scale
        self.symbol_outline_gap_scale = symbol_outline_gap_scale
        self.inradius_scale = inradius_scale
        self.quad_segs = quad_segs

        self._symbol_paths = []
        self._symbol_edgecolors = []
        self._symbol_facecolors = []
        self._symbol_linewidths = []

    def _get_symbol_parts(
        self, /,
        distance: float,
        inradius: float, incenter: Point
    ) -> Any:
        circle = shapely.geometry.Point(
            float(incenter.x), float(incenter.y)
        ).buffer(
            self.inradius_scale*inradius, quad_segs=self.quad_segs
        )

        y_max = incenter.y + inradius
        y_min = incenter.y - inradius

        rectangle = shapely.geometry.Polygon((
            (incenter.x-distance, y_min),
            (incenter.x-distance, y_max),
            (incenter.x+distance, y_max),
            (incenter.x+distance, y_min),
            (incenter.x-distance, y_min),
        ))
        return circle.difference(rectangle)

    def _prepare_symbol_parts(
        self, /,
        symbol_parts: Any, linewidth_points: float, delta: float,
        *, edgecolor: MPLColor, facecolor: MPLColor,
    ) -> None:
        already_done = 0
        if len(symbol_parts.geoms) != 2:
            print(len(symbol_parts.geoms), "symbol part(s) found, expected 2.")
        for geom in symbol_parts.geoms:
            try:
                smaller_geom = shapely.geometry.Polygon(
                    geom.exterior.offset_curve(
                        -delta,
                        quad_segs=self.quad_segs,
                        join_style=shapely.BufferJoinStyle.mitre
                    )
                )
                symbol_part = geom.difference(smaller_geom)
                path = Path.make_compound_path(*[
                    Path(np.asarray(shape.coords), closed=True)
                    for shape in (
                        symbol_part.exterior, *symbol_part.interiors
                    )
                ])
            except (
                shapely.GEOSException, ValueError,
                TypeError, AttributeError
            ):
                for _ in range(already_done):
                    del self._symbol_paths[-1]
                    del self._symbol_edgecolors[-1]
                    del self._symbol_facecolors[-1]
                    del self._symbol_linewidths[-1]
                return
            self._symbol_paths.append(path)
            self._symbol_edgecolors.append(edgecolor)
            self._symbol_facecolors.append(facecolor)
            self._symbol_linewidths.append(linewidth_points)
            already_done += 1

    def get_real_edgecolor(
        self, /, data: dict[str, Data], negative: bool
    ) -> MPLColor:
        edgecolor = (self.symbol_edgecolor
                     if not negative else
                     self.negative_symbol_edgecolor)
        if not isinstance(edgecolor, str):
            return edgecolor
        if edgecolor == 'data':
            key = (
                'symbol_edgecolor'
                if not negative else
                'negative_symbol_edgecolor'
            )
        elif edgecolor.startswith('data[') and edgecolor.endswith(']'):
            key = edgecolor[5:-1]
        else:
            return edgecolor
        return cast(ColorData[Color], data[key]).color.to_hex()
    
    def get_real_facecolor(
        self, /, data: dict[str, Data], negative: bool
    ) -> MPLColor:
        facecolor = (self.symbol_facecolor
                     if not negative else
                     self.negative_symbol_facecolor)
        if not isinstance(facecolor, str):
            return facecolor
        if facecolor == 'data':
            key = (
                'symbol_facecolor'
                if not negative else
                'negative_symbol_facecolor'
            )
        elif facecolor.startswith('data[') and facecolor.endswith(']'):
            key = facecolor[5:-1]
        else:
            return facecolor
        return cast(ColorData[Color], data[key]).color.to_hex()

    def prepare_symbol(
        self, /,
        triangle: Triangle,
        data: dict[str, Data],
        *, negative: bool,
    ) -> None:
        DATA = self.axes.transData
        FIGURE = self.figure.dpi_scale_trans
        edgecolor = self.get_real_edgecolor(data, negative)
        facecolor = self.get_real_facecolor(data, negative)
        if (
            is_mpl_color_transparent(edgecolor) and
            is_mpl_color_transparent(facecolor)
        ):
            return
        a, b, c = (triangle.b.dist(triangle.c),
                   triangle.a.dist(triangle.c),
                   triangle.a.dist(triangle.b))
        incenter = (a*triangle.a + b*triangle.b + c*triangle.c)/(a + b + c)
        inradius = float(
            0.5 * mp.sqrt(  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                (b+c-a) * (c+a-b) * (a+b-c) / (a+b+c)
            )
        )
        symbol_part_distance = (inradius *
                                self.inradius_scale *
                                self.symbol_part_distance_scale)
        symbol_outline_gap = (inradius *
                              self.inradius_scale *
                              self.symbol_outline_gap_scale)

        float_triangle = Triangle(
            *[Point(float(x), float(y))
              for x, y in triangle.coords.T]
        )
        p = [
            p.transform(DATA, FIGURE)
            for p in (float_triangle.a, float_triangle.b, float_triangle.c)
        ]
        min_side_length = min(
            [p[0].dist(p[1]), p[1].dist(p[2]), p[0].dist(p[2])]
        )
        linewidth_inches = self.linewidth_scale * min_side_length * 72
        symbol_parts = self._get_symbol_parts(symbol_part_distance,
                                              inradius, incenter)
        if not hasattr(symbol_parts, 'geoms'):
            return
        self._prepare_symbol_parts(symbol_parts, linewidth_inches,
                                   symbol_outline_gap, edgecolor=edgecolor,
                                   facecolor=facecolor)

    def commit_draw(self, /) -> None:
        symbol_patches = PatchCollection(
            [PathPatch(p) for p in self._symbol_paths],
            facecolors=self._symbol_facecolors,
            edgecolors=self._symbol_edgecolors,
            linewidths=self._symbol_linewidths,
            joinstyle='miter',
        )
        _ = self.axes.add_collection(symbol_patches)
    
    @override
    def root_draw_triangle(
        self, node: RootTriangleNode, /
    ) -> None:
        try:
            self.prepare_symbol(node.untransformed.triangle,
                                node.data,
                                negative=False)
        except ZeroDivisionError:
            pass
    
    @override
    def base_draw_triangle(
        self, node: BaseTriangleNode, /
    ) -> None:
        try:
            self.prepare_symbol(node.untransformed.triangle,
                                node.data,
                                negative=False)
        except ZeroDivisionError:
            pass
    
    @override
    def normal_draw_positive_triangle(
        self, node: NormalTriangleNode, /
    ) -> None:
        try:
            self.prepare_symbol(node.untransformed.triangle,
                                node.data,
                                negative=False)
        except ZeroDivisionError:
            pass
    
    @override
    def normal_draw_negative_triangle(
        self, node: NormalTriangleNode, /
    ) -> None:
        try:
            self.prepare_symbol(node.untransformed.negative_triangle,
                                node.data,
                                negative=True)
        except ZeroDivisionError:
            pass

    @override
    def draw_tree(self, /, tree: TriangleTree) -> None:
        super().draw_tree(tree)
        self.commit_draw()



