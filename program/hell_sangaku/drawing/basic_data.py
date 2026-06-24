from __future__ import annotations

from collections.abc import Mapping
from typing import ClassVar, Self, cast, get_args, override

from ..base.index import Index
from ..base.tree import (BaseSideNode, BaseTriangleNode, Data,
                         NormalTriangleNode, RootSideNode, RootTriangleNode,
                         TriangleTreeNode)
from ..base.types import NormalTriangleType
from .colors import Color


class ColorData[ColorType: Color](Data):
    """
    Color data assigns a color to each real node and to the circle.
    Root side nodes and base side nodes are skipped.

    The colors are computed as follows:
        if the index exists inside of predefined_colors it is used
        if the index does not exist inside of predefined_colors:
            - if it is the root triangle node, the circle color is used
            - if it is a root side node, the root data is copied
            - if it is a base side node, the base data is copied
            - if it is a base triangle node, the circle color and the
              parent color are mixed as defined by the color type
            - if it is a normal triangle node, the circle color, and the
              touching triangles' colors are mixed as defined by the
              color type

    The class may also specify weights for these mixings. A more
    advanced class may also compute the weights on the fly, but that
    was not necessary for this, so it was left as a class member.
    """
    # subclasses should define this
    predefined_colors: ClassVar[
        Mapping[Index, ColorType] # pyright: ignore[reportGeneralTypeIssues]
    ]
    # subclasses should define this
    circle_color: ClassVar[
        ColorType  # pyright: ignore[reportGeneralTypeIssues]
    ]
    
    # the weights to use for computations on a base triangle
    base_parent_weight: ClassVar[float] = 1
    base_circle_weight: ClassVar[float] = 1
    
    # the weights to use for computations on a horizontal normal
    # triangle
    horizontal_touching_vertical_weight: ClassVar[float] = 1
    horizontal_touching_horizontal_weight: ClassVar[float] = 1
    horizontal_circle_weight: ClassVar[float] = 1

    # the weights to use for computations on a vertical normal
    # triangle
    vertical_touching_vertical_weight: ClassVar[float] = 1
    vertical_touching_horizontal_weight: ClassVar[float] = 1
    vertical_circle_weight: ClassVar[float] = 1

    color: ColorType

    def __init__(self, /, color: ColorType):
        self.color = color
    
    @classmethod
    @override
    def create(cls, /, key: str, node: TriangleTreeNode) -> Self:
        if node.index in cls.predefined_colors:
            return cls(cls.predefined_colors[node.index])
        orig_base = getattr(cls, '__orig_bases__')[0]
        color_class = get_args(orig_base)[0]
        match node:
            case RootTriangleNode():
                return cls(cls.circle_color)
            case RootSideNode():
                return cls(cast(Self, node.parent.data[key]).color)
            case BaseSideNode():
                return cls(cast(Self, node.parent.data[key]).color)
            case BaseTriangleNode():
                if isinstance(node.parent, RootSideNode):
                    real_parent = node.parent.parent
                else:
                    real_parent = node.parent
                parent_color = cast(Self, real_parent.data[key]).color
                return cls(color_class.mix(
                    parent_color, cls.base_parent_weight,
                    cls.circle_color, cls.base_circle_weight
                ))
            case NormalTriangleNode(type=NormalTriangleType.HORIZONTAL):
                horizontal_touching_color = cast(
                    Self, node.touching_horizontal.data[key]
                ).color
                vertical_touching_color = cast(
                    Self, node.touching_vertical.data[key]
                ).color
                return cls(color_class.mix(
                    horizontal_touching_color,
                    cls.horizontal_touching_horizontal_weight,
                    vertical_touching_color,
                    cls.vertical_touching_horizontal_weight,
                    cls.circle_color, cls.horizontal_circle_weight
                ))
            case NormalTriangleNode(type=NormalTriangleType.VERTICAL):
                horizontal_touching_color = cast(
                    Self, node.touching_horizontal.data[key]
                ).color
                vertical_touching_color = cast(
                    Self, node.touching_vertical.data[key]
                ).color
                return cls(color_class.mix(
                    horizontal_touching_color,
                    cls.vertical_touching_horizontal_weight,
                    vertical_touching_color,
                    cls.vertical_touching_horizontal_weight,
                    cls.circle_color, cls.vertical_circle_weight
                ))
            case _:
                assert False

