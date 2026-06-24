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


class Figure5(Processor):
    
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
        with Timer() as timer, timer.pushed("Outline"):
            with timer.pushed("Calculating"):
                _ = self.tree.calculate_tree(30, 1)
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
                    a = node.untransformed.triangle.a
                    b = node.untransformed.triangle.b
                    c = node.untransformed.triangle.c
                    center = (a + b + c)/3
                    _ = self.axes.plot(  # pyright: ignore[reportUnknownMemberType]
                        *node.untransformed.triangle.draw_coords,
                        color='black',
                        linewidth=1
                    )
                    # random heuristic to try to keep the annotation
                    # inside the triangle
                    side_length = node.untransformed.triangle.a.dist(
                        node.untransformed.triangle.b
                    )
                    index = str(node.index)
                    index_length = (
                        0.5 * (
                            index.count('a') +
                            index.count('b') +
                            index.count('c') +
                            index.count('l') +
                            index.count('r')
                        ) + (
                            index.count('R') +
                            index.count('B') +
                            index.count('H') +
                            index.count('V')
                        )
                    )
                    fontsize = side_length*144 - index_length
                    _ = self.axes.annotate(  # pyright: ignore[reportUnknownMemberType]
                        fr"$\triangle_{{{str(node.index)}}}$",
                        (center.x, center.y),
                        ha='center',
                        va='center',
                        fontsize=fontsize,
                        usetex=True
                    )
            with timer.pushed("Saving"):
                self.figure.savefig(  # pyright: ignore[reportUnknownMemberType]
                    self.output, pad_inches=0
                )
