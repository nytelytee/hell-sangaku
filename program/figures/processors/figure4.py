from __future__ import annotations

from typing import override

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpmath import mp  # pyright: ignore[reportMissingTypeStubs]

from hell_sangaku.base.tree import BaseSideNode, RootTriangleNode, TriangleTree

from ..processor import Processor
from ..timer import Timer


class Figure4(Processor):
    
    output: str
    figsize: float
    tree: TriangleTree
    figure: Figure
    axes: Axes

    def __init__(
        self, *, output: str, figsize: float = 20.48,
    ) -> None:
        self.output = output
        self.figsize = figsize
        radius = 1
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
        with Timer() as timer, timer.pushed("Figure 4"):
            with timer.pushed("Calculating"):
                _ = (
                    self.tree
                    .calculate_root()
                    .calculate_c()
                    .calculate_base()
                    .calculate_left()
                    .calculate_horizontal()
                )
            with timer.pushed("Drawing"):
                assert self.tree.root is not None
                assert self.tree.root.c is not None
                assert self.tree.root.c.base is not None
                assert self.tree.root.c.base.left is not None
                assert self.tree.root.c.base.left.horizontal is not None
                circle_angle = np.linspace(0, 2*np.pi, 1000)
                x = np.cos(circle_angle)
                y = np.sin(circle_angle)
                _ = self.axes.plot(  # pyright: ignore[reportUnknownMemberType]
                    x, y, color='black'
                )
                for node in self.tree.walk():
                    if isinstance(node, (RootTriangleNode, BaseSideNode)):
                        continue
                    _ = self.axes.plot(  # pyright: ignore[reportUnknownMemberType]
                        *node.transformed.triangle.draw_coords,
                        color='black',
                        linewidth=1
                    )
            with timer.pushed("Saving"):
                self.figure.savefig(  # pyright: ignore[reportUnknownMemberType]
                    self.output, pad_inches=0
                )
