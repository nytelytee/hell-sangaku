from __future__ import annotations

from typing import cast, override

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpmath import mp  # pyright: ignore[reportMissingTypeStubs]

from hell_sangaku.base.tree import TriangleTree
from hell_sangaku.base.types import RealNumber
from hell_sangaku.drawing.basic_drawers import CompoundDrawer
from hell_sangaku.drawing.drawer import Drawer

from ..data.main import (MainProfilePictureMainTriangleData,
                         MainProfilePictureMainTriangleSymbolData,
                         MainProfilePictureNegativeTriangleData,
                         MainProfilePictureNegativeTriangleSymbolData)
from ..drawers.main_triangle_drawer import MainTriangleDrawer
from ..drawers.outline_drawer import OutlineDrawer
from ..drawers.symbol_drawer import SymbolDrawer
from ..drawers.uncovered_area_drawer import UncoveredAreaDrawer
from ..processor import Processor
from ..timer import Timer


class MainProfilePicture(Processor):
    
    output: str
    figsize: float
    max_triangles: int
    max_base_levels: int
    tree: TriangleTree
    figure: Figure
    axes: Axes
    drawer: Drawer

    def __init__(
        self, *, output: str, figsize: float = 204.8,
        max_triangles: int = 100000,
        max_base_levels: int = 2,
        alt: bool = False,
    ) -> None:
        self.output = output
        self.figsize = figsize
        self.max_base_levels = max_base_levels
        self.max_triangles = max_triangles
        radius = 1
        beta = cast(
            RealNumber, mp.atan(2)  # pyright: ignore[reportUnknownMemberType]
        )
        alpha = mp.pi - 2*beta
        if alt:
            self.tree = TriangleTree(
                alpha, beta,
                color2=MainProfilePictureMainTriangleData,
                color=MainProfilePictureNegativeTriangleData,
                negative_symbol_facecolor=(
                    MainProfilePictureMainTriangleSymbolData
                ),
                symbol_facecolor=(
                    MainProfilePictureNegativeTriangleSymbolData
                )
            )
        else:
            self.tree = TriangleTree(
                alpha, beta,
                color=MainProfilePictureMainTriangleData,
                color2=MainProfilePictureNegativeTriangleData,
                symbol_facecolor=MainProfilePictureMainTriangleSymbolData,
                negative_symbol_facecolor=(
                    MainProfilePictureNegativeTriangleSymbolData
                )
            )
        self.figure = plt.figure(  # pyright: ignore[reportUnknownMemberType]
            figsize=(figsize, figsize)
        )
        self.axes = Axes(self.figure, (0, 0, 1, 1))
        _ = self.axes.set_xlim(left=-radius, right=radius)
        _ = self.axes.set_ylim(bottom=-radius, top=radius)
        self.axes.set_axis_off()
        _ = self.figure.add_axes(  # pyright: ignore[reportUnknownMemberType]
            self.axes
        )
        _ = self.axes.margins(0, 0)
        self.drawer = CompoundDrawer(
            MainTriangleDrawer(self.figure, self.axes, key='color'),
            UncoveredAreaDrawer(self.figure, self.axes, key='color2'),
            OutlineDrawer(self.figure, self.axes),
            SymbolDrawer(
                self.figure, self.axes, symbol_edgecolor='white',
                symbol_facecolor='data',
                negative_symbol_facecolor='data',
            )
        )

    @override
    def process(self) -> None:
        with Timer() as timer, timer.pushed("Main"):
            with timer.pushed("Calculating"):
                self.tree.calculate_tree(
                    self.max_triangles,
                    self.max_base_levels
                )
                print(f"Calculated {self.max_triangles} triangles.")

            with timer.pushed("Drawing"):
                self.drawer.draw_tree(self.tree)

            with timer.pushed("Saving"):
                self.figure.savefig(  # pyright: ignore[reportUnknownMemberType]
                    self.output, pad_inches=0
                )
