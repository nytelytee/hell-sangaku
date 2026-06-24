from typing import override

from hell_sangaku.base.tree import (BaseTriangleNode, NormalTriangleNode,
                                    RootTriangleNode)
from hell_sangaku.drawing.basic_drawers import ColorDataDrawer


class UncoveredAreaDrawer(ColorDataDrawer):
    
    @override
    def normal_should_draw_positive_triangle(
        self, _node: NormalTriangleNode, /
    ):
        return False
    
    @override
    def base_should_draw_triangle(
        self, _node: BaseTriangleNode, /
    ):
        return False

    @override
    def root_should_draw_triangle(
        self, _node: RootTriangleNode, /
    ):
        return False
