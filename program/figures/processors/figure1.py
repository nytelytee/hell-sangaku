from __future__ import annotations

from typing import override

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpmath import mp  # pyright: ignore[reportMissingTypeStubs]

from hell_sangaku.base.tree import BaseSideNode, RootSideNode, TriangleTree

from ..processor import Processor
from ..timer import Timer


class Figure1(Processor):
    
    output: str
    figsize: float
    max_triangles: int
    max_base_levels: int
    tree: TriangleTree
    figure: Figure
    axes: Axes

    def __init__(
        self, *,
        output: str,
        figsize: float = 20.48,
        max_triangles: int = 2000,
        max_base_levels: int = 2
    ) -> None:
        self.output = output
        self.figsize = figsize
        radius = 1
        self.max_base_levels = max_base_levels
        self.max_triangles = max_triangles
        self.tree = TriangleTree(mp.pi/3, mp.pi/3)
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

    @override
    def process(self) -> None:
        with Timer() as timer, timer.pushed("Figure 1"):
            with timer.pushed("Calculating"):
                self.tree.calculate_tree(
                    self.max_triangles,
                    self.max_base_levels
                )
                print(f"Calculated {self.max_triangles} triangles.")
            with timer.pushed("Drawing"):
                circle_angle = np.linspace(0, 2*np.pi, 1000)
                x = np.cos(circle_angle)
                y = np.sin(circle_angle)
                _ = self.axes.plot(  # pyright: ignore[reportUnknownMemberType]
                    x, y, color='black'
                )
                for node in self.tree.walk():
                    if isinstance(node, (RootSideNode, BaseSideNode)):
                        continue
                    linewidth = 1
                    if len(node.index.parts) > 6:
                        linewidth *= 5/len(node.index.parts)
                    _ = self.axes.plot(  # pyright: ignore[reportUnknownMemberType]
                        *node.untransformed.triangle.draw_coords,
                        color='black',
                        linewidth=linewidth
                    )

            with timer.pushed("Saving"):
                self.figure.savefig(  # pyright: ignore[reportUnknownMemberType]
                    self.output, pad_inches=0
                )
