from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, cast, final, override

from ..base.tree import (BaseSideNode, BaseTriangleNode, NormalTriangleNode,
                         RootSideNode, RootTriangleNode, TriangleTree,
                         TriangleTreeNode)
from ..base.types import MPLColor
from ..drawing.colors import Color
from ..drawing.drawer import Drawer
from .basic_data import ColorData

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


class SplitFilteringDrawer(Drawer):
    """
    This drawer splits each primitive shape into its own function and
    allows for filtering whether or not to draw a node based on some
    predicate.
    """

    def should_draw_node(self, _node: TriangleTreeNode, /) -> bool:
        return True

    def root_should_draw_triangle(self, _node: RootTriangleNode, /) -> bool:
        return True
    
    def root_should_draw_segment_a(self, _node: RootTriangleNode, /) -> bool:
        return True
    
    def root_should_draw_segment_b(self, _node: RootTriangleNode, /) -> bool:
        return True
    
    def root_should_draw_segment_c(self, _node: RootTriangleNode, /) -> bool:
        return True

    def base_should_draw_triangle(self, _node: BaseTriangleNode, /) -> bool:
        return True
    
    def base_should_draw_segment(self, _node: BaseTriangleNode, /) -> bool:
        return True

    def base_side_should_draw_pseudo_sector(
        self, _node: BaseSideNode, /
    ) -> bool:
        return True

    def normal_should_draw_positive_triangle(
        self, _node: NormalTriangleNode, /
    ) -> bool:
        return True
    
    def normal_should_draw_negative_triangle(
        self, _node: NormalTriangleNode, /
    ) -> bool:
        return True
    
    def normal_should_draw_horizontal_pseudo_sector(
        self, _node: NormalTriangleNode, /
    ) -> bool:
        return True
    
    def normal_should_draw_vertical_pseudo_sector(
        self, _node: NormalTriangleNode, /
    ) -> bool:
        return True
    
    def root_draw_triangle(self, _node: RootTriangleNode, /) -> None:
        pass
    
    def root_draw_segment_a(self, _node: RootTriangleNode, /) -> None:
        pass
    
    def root_draw_segment_b(self, _node: RootTriangleNode, /) -> None:
        pass
    
    def root_draw_segment_c(self, _node: RootTriangleNode, /) -> None:
        pass
    
    def base_draw_triangle(self, _node: BaseTriangleNode, /) -> None:
        pass
    
    def base_draw_segment(self, _node: BaseTriangleNode, /) -> None:
        pass

    def base_side_draw_pseudo_sector(self, _node: BaseSideNode, /) -> None:
        pass

    def normal_draw_positive_triangle(
        self, _node: NormalTriangleNode, /
    ) -> None:
        pass
    
    def normal_draw_negative_triangle(
        self, _node: NormalTriangleNode, /
    ) -> None:
        pass
    
    def normal_draw_horizontal_pseudo_sector(
        self, _node: NormalTriangleNode, /
    ) -> None:
        pass
    
    def normal_draw_vertical_pseudo_sector(
        self, _node: NormalTriangleNode, /
    ) -> None:
        pass

    @final
    @override
    def draw_node(self, node: TriangleTreeNode, /) -> None:
        if not self.should_draw_node(node):
            return
        match node:
            case RootTriangleNode():
                if self.root_should_draw_triangle(node):
                    self.root_draw_triangle(node)
                if self.root_should_draw_segment_a(node):
                    self.root_draw_segment_a(node)
                if self.root_should_draw_segment_b(node):
                    self.root_draw_segment_b(node)
                if self.root_should_draw_segment_c(node):
                    self.root_draw_segment_c(node)
            case BaseTriangleNode():
                if self.base_should_draw_triangle(node):
                    self.base_draw_triangle(node)
                if self.base_should_draw_segment(node):
                    self.base_draw_segment(node)
            case BaseSideNode():
                if self.base_side_should_draw_pseudo_sector(node):
                    self.base_side_draw_pseudo_sector(node)
            case NormalTriangleNode():
                if self.normal_should_draw_positive_triangle(node):
                    self.normal_draw_positive_triangle(node)
                if self.normal_should_draw_negative_triangle(node):
                    self.normal_draw_negative_triangle(node)
                if self.normal_should_draw_horizontal_pseudo_sector(node):
                    self.normal_draw_horizontal_pseudo_sector(node)
                if self.normal_should_draw_vertical_pseudo_sector(node):
                    self.normal_draw_vertical_pseudo_sector(node)
            case RootSideNode():
                pass


class DefaultFilteringDrawer(SplitFilteringDrawer):
    """
    The default filters allow a portion to be drawn if the area it will
    fill will not contain any children nodes.
    """
    
    @override
    def root_should_draw_segment_a(self, node: RootTriangleNode, /) -> bool:
        return node.a is None or node.a.base is None
    
    @override
    def root_should_draw_segment_b(self, node: RootTriangleNode, /) -> bool:
        return node.b is None or node.b.base is None
    
    @override
    def root_should_draw_segment_c(self, node: RootTriangleNode, /) -> bool:
        return node.c is None or node.c.base is None

    @override
    def base_should_draw_segment(self, node: BaseTriangleNode, /) -> bool:
        return node.base is None

    @override
    def base_side_should_draw_pseudo_sector(
        self, node: BaseSideNode, /
    ) -> bool:
        return node.horizontal is None
    
    @override
    def normal_should_draw_horizontal_pseudo_sector(
        self, node: NormalTriangleNode, /
    ) -> bool:
        return node.horizontal is None
    
    @override
    def normal_should_draw_vertical_pseudo_sector(
        self, node: NormalTriangleNode, /
    ) -> bool:
        return node.vertical is None


class MatplotlibDrawer(Drawer, ABC):

    figure: Figure
    axes: Axes
    
    def __init__(self, figure: Figure, axes: Axes) -> None:
        self.figure = figure
        self.axes = axes

class ColorDrawer(MatplotlibDrawer, DefaultFilteringDrawer):
    """
    A matplotlib drawer that will fill the area with a color given
    by a method.
    """

    def root_triangle_color(
        self, _node: RootTriangleNode, /
    ) -> MPLColor:
        raise NotImplementedError
    
    def root_segment_a_color(
        self, _node: RootTriangleNode, /
    ) -> MPLColor:
        raise NotImplementedError
    
    def root_segment_b_color(
        self, _node: RootTriangleNode, /
    ) -> MPLColor:
        raise NotImplementedError
    
    def root_segment_c_color(
        self, _node: RootTriangleNode, /
    ) -> MPLColor:
        raise NotImplementedError

    def base_triangle_color(
        self, _node: BaseTriangleNode, /
    ) -> MPLColor:
        raise NotImplementedError
    
    def base_segment_color(
        self, _node: BaseTriangleNode, /
    ) -> MPLColor:
        raise NotImplementedError

    def base_side_pseudo_sector_color(
        self, _node: BaseSideNode, /
    ) -> MPLColor:
        raise NotImplementedError

    def normal_positive_triangle_color(
        self, _node: NormalTriangleNode, /
    ) -> MPLColor:
        raise NotImplementedError
    
    def normal_negative_triangle_color(
        self, _node: NormalTriangleNode, /
    ) -> MPLColor:
        raise NotImplementedError

    def normal_horizontal_pseudo_sector_color(
        self, _node: NormalTriangleNode, /
    ) -> MPLColor:
        raise NotImplementedError
    
    def normal_vertical_pseudo_sector_color(
        self, _node: NormalTriangleNode, /
    ) -> MPLColor:
        raise NotImplementedError
    
    @override
    def root_draw_triangle(self, node: RootTriangleNode, /) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.triangle.draw_coords,
            facecolor=self.root_triangle_color(node)
        )
    
    @override
    def root_draw_segment_a(self, node: RootTriangleNode, /) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.a_segment.draw_coords,
            facecolor=self.root_segment_a_color(node)
        )
    
    @override
    def root_draw_segment_b(self, node: RootTriangleNode, /) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.b_segment.draw_coords,
            facecolor=self.root_segment_b_color(node)
        )
    
    @override
    def root_draw_segment_c(self, node: RootTriangleNode, /) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.c_segment.draw_coords,
            facecolor=self.root_segment_c_color(node)
        )

    @override
    def base_draw_triangle(self, node: BaseTriangleNode, /) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.triangle.draw_coords,
            facecolor=self.base_triangle_color(node)
        )

    @override
    def base_draw_segment(self, node: BaseTriangleNode, /) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.segment.draw_coords,
            facecolor=self.base_segment_color(node)
        )
    
    @override
    def base_side_draw_pseudo_sector(
        self, node: BaseSideNode, /
    ) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.pseudo_sector.draw_coords,
            facecolor=self.base_side_pseudo_sector_color(node)
        )
    
    @override
    def normal_draw_positive_triangle(
        self, node: NormalTriangleNode, /
    ) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.triangle.draw_coords,
            facecolor=self.normal_positive_triangle_color(node)
        )
    
    @override
    def normal_draw_negative_triangle(
        self, node: NormalTriangleNode, /
    ) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.negative_triangle.draw_coords,
            facecolor=self.normal_negative_triangle_color(node)
        )
    
    @override
    def normal_draw_horizontal_pseudo_sector(
        self, node: NormalTriangleNode, /
    ) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.horizontal_pseudo_sector.draw_coords,
            facecolor=self.normal_horizontal_pseudo_sector_color(node)
        )
    
    @override
    def normal_draw_vertical_pseudo_sector(
        self, node: NormalTriangleNode, /
    ) -> None:
        _ = self.axes.fill(  # pyright: ignore[reportUnknownMemberType]
            *node.untransformed.vertical_pseudo_sector.draw_coords,
            facecolor=self.normal_vertical_pseudo_sector_color(node)
        )


class ColorDataDrawer(ColorDrawer):
    """
    A matplotlib drawer that will fill the area with some data from
    the node's attached data.
    """

    key: str

    def __init__(
        self,
        figure: Figure,
        axes: Axes,
        key: str = "color"
    ) -> None:
        super().__init__(figure, axes)
        self.key = key
    
    @override
    def root_triangle_color(
        self, node: RootTriangleNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()

    @override
    def root_segment_a_color(
        self, node: RootTriangleNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()
    
    @override
    def root_segment_b_color(
        self, node: RootTriangleNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()
    
    @override
    def root_segment_c_color(
        self, node: RootTriangleNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()

    @override
    def base_triangle_color(
        self, node: BaseTriangleNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()
    
    @override
    def base_segment_color(
        self, node: BaseTriangleNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()

    @override
    def base_side_pseudo_sector_color(
        self, node: BaseSideNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()

    @override
    def normal_positive_triangle_color(
        self, node: NormalTriangleNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()
    
    @override
    def normal_negative_triangle_color(
        self, node: NormalTriangleNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()

    @override
    def normal_horizontal_pseudo_sector_color(
        self, node: NormalTriangleNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()
    
    @override
    def normal_vertical_pseudo_sector_color(
        self, node: NormalTriangleNode, /
    ) -> MPLColor:
        return cast(ColorData[Color], node.data[self.key]).color.to_hex()

class CompoundDrawer(Drawer):

    drawers: tuple[Drawer, ...]

    def __init__(self, *drawers: Drawer):
        self.drawers = drawers
    
    @override
    def draw_node(self, node: TriangleTreeNode, /) -> None:
        for drawer in self.drawers:
            drawer.draw_node(node)
    
    @override
    def draw_tree(self, tree: TriangleTree, /) -> None:
        for drawer in self.drawers:
            drawer.draw_tree(tree)
