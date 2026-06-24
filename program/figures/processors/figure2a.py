from __future__ import annotations

from typing import override

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from mpmath import mp  # pyright: ignore[reportMissingTypeStubs]

from hell_sangaku.base.tree import TriangleTree

from ..processor import Processor
from ..timer import Timer


class Figure2a(Processor):
    
    output: str
    figsize: float
    max_triangles: int
    max_base_levels: int
    tree: TriangleTree
    figure: Figure
    axes: Axes

    def __init__(
        self,
        *,
        output: str,
        figsize: float = 20.48
    ) -> None:
        self.output = output
        self.figsize = figsize
        radius = 1
        self.tree = TriangleTree(mp.pi/3, mp.pi/3, 0)
        self.figure = plt.figure(  # pyright: ignore[reportUnknownMemberType]
            figsize=(figsize, figsize)
        )
        self.axes = Axes(self.figure, (0, 0, 1, 1))
        _ = self.axes.set_xlim(left=-radius-0.2, right=radius+0.2)
        _ = self.axes.set_ylim(bottom=-radius-0.2, top=radius+0.2)
        self.axes.set_axis_off()
        _ = self.figure.add_axes(  # pyright: ignore[reportUnknownMemberType]
            self.axes
        )
        _ = self.axes.margins(0, 0)

    @override
    def process(self) -> None:
        with Timer() as timer, timer.pushed("Figure 2a"):
            with timer.pushed("Calculating"):
                _ = self.tree.calculate_root()
            with timer.pushed("Drawing"):
                assert self.tree.root is not None
                circle_angle = np.linspace(0, 2*np.pi, 1000)
                x = np.cos(circle_angle)
                y = np.sin(circle_angle)
                _ = self.axes.plot(  # pyright: ignore[reportUnknownMemberType]
                    x, y, color='black'
                )
                _ = self.axes.plot(  # pyright: ignore[reportUnknownMemberType]
                    *self.tree.root.untransformed.triangle.draw_coords,
                    color='black',
                    linewidth=1
                )
                text = ("A", "B", "C")
                offx = (0.15, 0, 0)
                offy = (0.05, 0.15, -0.05)
                for i, text in enumerate(text):
                    tx = self.tree.root.untransformed.triangle.coords[0][i] 
                    ty = self.tree.root.untransformed.triangle.coords[1][i] 
                    _ = self.axes.annotate(  # pyright: ignore[reportUnknownMemberType]
                        text,
                        (tx + offx[i], ty + offy[i]),
                        color='black',
                        fontsize=100,
                        usetex=True,
                        ha='right',
                        va='top'
                    )
            with timer.pushed("Saving"):
                self.figure.savefig(  # pyright: ignore[reportUnknownMemberType]
                    self.output, pad_inches=0
                )
