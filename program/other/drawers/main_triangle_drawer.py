from __future__ import annotations

from typing import override

from hell_sangaku.base.tree import (BaseSideNode, BaseTriangleNode,
                                    NormalTriangleNode, RootTriangleNode)
from hell_sangaku.drawing.basic_drawers import ColorDataDrawer


class MainTriangleDrawer(ColorDataDrawer):
    
    @override
    def normal_should_draw_negative_triangle(
        self, _node: NormalTriangleNode, /
    ):
        return False
    
    @override
    def normal_should_draw_horizontal_pseudo_sector(
        self, _node: NormalTriangleNode, /
    ):
        return False

    @override
    def normal_should_draw_vertical_pseudo_sector(
        self, _node: NormalTriangleNode, /
    ):
        return False
    
    @override
    def base_side_should_draw_pseudo_sector(
        self, _node: BaseSideNode, /
    ):
        return False
    
    @override
    def base_should_draw_segment(
        self, node: BaseTriangleNode, /
    ):
        return False

    @override
    def root_should_draw_segment_a(
        self, _node: RootTriangleNode, /
    ):
        return False

    @override
    def root_should_draw_segment_b(
        self, _node: RootTriangleNode, /
    ):
        return False

    @override
    def root_should_draw_segment_c(
        self, _node: RootTriangleNode, /
    ):
        return False
