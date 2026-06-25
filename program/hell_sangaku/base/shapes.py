from __future__ import annotations

from dataclasses import dataclass
from math import prod
from operator import attrgetter
from typing import Any, Self, cast, override

import mpmath  # pyright: ignore[reportMissingTypeStubs]
import numpy as np
from matplotlib.transforms import IdentityTransform, Transform
from mpmath import mp  # pyright: ignore[reportMissingTypeStubs]
from numpy.typing import NDArray

from .types import BaseSideType, RealNumber, RootSideType


@dataclass(frozen=True)
class Point:
    """
    A point in 2D space.
    
    Members:
        x : the x coordinate
        y : the y coordinate
    """

    x: RealNumber
    y: RealNumber

    @classmethod
    def fromarray(cls, /, array: NDArray[Any]) -> Self:
        assert np.shape(array) == (2,)
        return cls(array[0], array[1])
    
    @override
    def __str__(self, /) -> str:
        return f"{float(self.x):.5f}, {float(self.y):.5f}"

    @property
    def angle(self) -> RealNumber:
        return cast(
            RealNumber,
            mpmath.arg(  # pyright: ignore[reportUnknownMemberType]
                self.x + 1j*self.y
            )
        )

    def __add__(self, other: Point, /) -> Self:
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self, /) -> Self:
        return self.__class__(self.x - other.x, self.y - other.y)

    def __mul__(self, other: RealNumber, /) -> Self:
        return self.__class__(self.x * other, self.y * other)

    def __rmul__(self, other: RealNumber, /) -> Self:
        return self.__class__(other * self.x, other * self.y)

    def __truediv__(self, other: RealNumber, /) -> Self:
        return self.__class__(self.x / other, self.y / other)

    def rotate(
        self, angle: RealNumber, /,
        *, around: Self | None = None
    ) -> Self:
        around_ = around or ORIGIN

        s, c = (
            mp.sin(angle),  # pyright: ignore[reportUnknownMemberType]
            mp.cos(angle)   # pyright: ignore[reportUnknownMemberType]
        )
        rotation_matrix = np.array(((c, s), (-s, c)), dtype=object).T

        x = self.x
        y = self.y

        x -= around_.x
        y -= around_.y

        coords = np.dot(rotation_matrix, ((x,), (y,)))
        x = coords[0][0]
        y = coords[1][0]

        x += around_.x
        y += around_.y

        return self.__class__(x, y)

    def dist(self, other: Self | None = None, /) -> RealNumber:
        otherx = other.x if other else 0
        othery = other.y if other else 0
        return cast(
            RealNumber, mp.sqrt(  # pyright: ignore[reportUnknownMemberType]
                (self.x-otherx)**2 + (self.y-othery)**2
            )
        )

    def transform(
        self, /,
        transform_from: Transform | None = None,
        transform_to: Transform | None = None,
    ) -> Self:
        tfrom = transform_from or IdentityTransform()
        tto = (transform_to or IdentityTransform()).inverted()
        x, y = tto.transform(
            tfrom.transform((self.x, self.y))  # type: ignore
        )
        return self.__class__(x, y)

    def coord(self, /) -> tuple[RealNumber, RealNumber]:
        return float(self.x), float(self.y)

    def normalize(self, /) -> Self:
        return self / self.dist()

    def rotate90(self, /) -> Self:
        return self.__class__(-self.y, self.x)

    def rotate180(self, /) -> Self:
        return self.__class__(-self.x, -self.y)

    def rotate270(self, /) -> Self:
        return self.__class__(self.y, -self.x)

    def dot(self, /, *others: Point) -> RealNumber:
        return (self.x*prod(map(attrgetter('x'), others)) +
                self.y*prod(map(attrgetter('y'), others)))


ORIGIN = Point(0, 0)
NAN_POINT = Point(float('nan'), float('nan'))


@dataclass(frozen=True)
class Triangle:
    """
    A collection of 3 points assumed to be in counter-clockwise winding.

    Members:
        a : the first point
        b : the second point
        c : the third point
    """

    a: Point
    b: Point
    c: Point


    @property
    def draw_coords(self) -> NDArray[Any]:
        return np.array(((self.a.x, self.b.x, self.c.x, self.a.x),
                         (self.a.y, self.b.y, self.c.y, self.a.y)),
                        dtype=object)
    
    @property
    def coords(self) -> NDArray[Any]:
        return np.array(((self.a.x, self.b.x, self.c.x),
                         (self.a.y, self.b.y, self.c.y)),
                        dtype=object)

    def rotate(
        self, angle: RealNumber, /,
        *, around: Point = ORIGIN,
    ) -> Self:

        coords = np.array(((self.a.x, self.b.x, self.c.x),
                          (self.a.y, self.b.y, self.c.y)),
                          dtype=object)
        s, c = (
            mp.sin(angle),  # pyright: ignore[reportUnknownMemberType]
            mp.cos(angle)   # pyright: ignore[reportUnknownMemberType]
        )
        rotation_matrix = np.array(((c, s), (-s, c)), dtype=object).T

        coords[0] -= around.x
        coords[1] -= around.y

        coords = np.dot(rotation_matrix, coords)

        coords[0] += around.x
        coords[1] += around.y

        return self.__class__(
            Point(coords[0][0], coords[1][0]),
            Point(coords[0][1], coords[1][1]),
            Point(coords[0][2], coords[1][2])
        )
    
    @override
    def __str__(self, /) -> str:
        return (f"{self.__class__.__name__}("
                f"A({self.a}), "
                f"B({self.b}), "
                f"C({self.c}))")


@dataclass(frozen=True)
class PositiveTriangle(Triangle):
    """
    Type representing upwards facing triangles in view transformations.

    Members:
        a : the original a point
        b : the original b point
        c : the original c point
        top : the top point
        left : the left point
        right : the right point
    """
    top: Point
    left: Point
    right: Point
    
    @classmethod
    def from_triangle(
        cls, triangle: Triangle, view_type: RootSideType
    ) -> Self:
        if view_type == RootSideType.A:
            return cls(
                triangle.a, triangle.b, triangle.c,
                triangle.a, triangle.b, triangle.c,
            )
        elif view_type == RootSideType.B:
            return cls(
                triangle.a, triangle.b, triangle.c,
                triangle.b, triangle.c, triangle.a,
            )
        elif view_type == RootSideType.C:
            return cls(
                triangle.a, triangle.b, triangle.c,
                triangle.c, triangle.a, triangle.b,
            )
    
    @classmethod
    def from_top_left_right(
        cls,
        top: Point, left: Point, right: Point,
        view_type: RootSideType
    ) -> Self:
        if view_type == RootSideType.A:
            # TLR = ABC
            return cls(
                top, left, right,
                top, left, right,
            )
        elif view_type == RootSideType.B:
            # TLR = BCA
            return cls(
                right, top, left,
                top, left, right,
            )
        elif view_type == RootSideType.C:
            # TLR = CAB
            return cls(
                left, right, top,
                top, left, right,
            )

    @override 
    def rotate(
        self, angle: RealNumber, /,
        *, around: Point = ORIGIN,
    ) -> Self:

        coords = np.array(
            (
                (
                    self.a.x, self.b.x, self.c.x,
                    self.top.x, self.left.x, self.right.x,
                ),
                (
                    self.a.y, self.b.y, self.c.y,
                    self.top.y, self.left.y, self.right.y,
                )
            ),
            dtype=object
        )

        s, c = (
            mp.sin(angle),  # pyright: ignore[reportUnknownMemberType]
            mp.cos(angle)   # pyright: ignore[reportUnknownMemberType]
        )
        rotation_matrix = np.array(((c, s), (-s, c)), dtype=object).T

        coords[0] -= around.x
        coords[1] -= around.y

        coords = np.dot(rotation_matrix, coords)

        coords[0] += around.x
        coords[1] += around.y

        return self.__class__(
            Point(coords[0][0], coords[1][0]),
            Point(coords[0][1], coords[1][1]),
            Point(coords[0][2], coords[1][2]),
            Point(coords[0][3], coords[1][3]),
            Point(coords[0][4], coords[1][4]),
            Point(coords[0][5], coords[1][5])
        )
    
    @override
    def __str__(self, /) -> str:
        return (
            f"{self.__class__.__name__}("
            f"T({self.top}), "
            f"L({self.left}), "
            f"R({self.right}))"
        )


@dataclass(frozen=True)
class NegativeTriangle(Triangle):
    """
    Type representing downwards facing triangles in view
    transformations.

    Members:
        a : the original a point
        b : the original b point
        c : the original c point
        bottom : the bottom point
        right : the right point
        left : the left point
    """
    bottom: Point
    right: Point
    left: Point

    @classmethod
    def from_positive_triangle(
        cls, triangle: PositiveTriangle, side_type: BaseSideType
    ) -> Self:
        rotation_side_point = (triangle.right
                               if side_type == BaseSideType.LEFT else
                               triangle.left)
        rotation_center = 0.5*(triangle.top + rotation_side_point)
        a = 2*rotation_center - triangle.a
        b = 2*rotation_center - triangle.b
        c = 2*rotation_center - triangle.c
        bottom = 2*rotation_center - triangle.top
        right = 2*rotation_center - triangle.left
        left = 2*rotation_center - triangle.right
        return cls(a, b, c, bottom, right, left)
    
    @override
    def rotate(
        self, angle: RealNumber, /,
        *, around: Point = ORIGIN,
    ) -> Self:

        coords = np.array(
            (
                (
                    self.a.x, self.b.x, self.c.x,
                    self.bottom.x, self.right.x, self.left.x,
                ),
                (
                    self.a.y, self.b.y, self.c.y,
                    self.bottom.y, self.right.y, self.left.y,
                )
            ),
            dtype=object
        )

        s, c = (
            mp.sin(angle),  # pyright: ignore[reportUnknownMemberType]
            mp.cos(angle)   # pyright: ignore[reportUnknownMemberType]
        )
        rotation_matrix = np.array(((c, s), (-s, c)), dtype=object).T

        coords[0] -= around.x
        coords[1] -= around.y

        coords = np.dot(rotation_matrix, coords)

        coords[0] += around.x
        coords[1] += around.y

        return self.__class__(
            Point(coords[0][0], coords[1][0]),
            Point(coords[0][1], coords[1][1]),
            Point(coords[0][2], coords[1][2]),
            Point(coords[0][3], coords[1][3]),
            Point(coords[0][4], coords[1][4]),
            Point(coords[0][5], coords[1][5])
        )

    @override
    def __str__(self, /) -> str:
        return (
            f"{self.__class__.__name__}("
            f"B({self.bottom}), "
            f"R({self.right}), "
            f"L({self.left}))"
        )


@dataclass(frozen=True)
class PseudoSector:
    """
    Shape bounded by an arc on a circle and point inside the circle.
    The circle is centered in the origin.

    It is called a pseudo-sector because the point does not have to be
    the center of the circle.

    Members:
        point : the point bounding the pseudo-sector
        angle_start : the starting angle of the arc bounding the
                      pseudo-sector
        angle_end : the ending angle of the arc bounding the
                    pseudo-sector
        radius : the radius of the circle
    """
    point: Point
    angle_start: RealNumber
    angle_end: RealNumber
    radius: RealNumber

    def rotate(self, angle: RealNumber, /) -> Self:
        angle_start = self.angle_start
        angle_end = self.angle_end
        new_point = self.point.rotate(angle)
        angle_start += angle
        angle_end += angle

        if angle_start > angle_end:
            #angle_end += 2*mp.pi
            angle_start, angle_end = angle_end, angle_start

        return self.__class__(new_point, angle_start, angle_end, self.radius)

    @property
    def coords(self) -> NDArray[Any]:
        angles = np.linspace(float(self.angle_start), float(self.angle_end))
        r = self.radius
        x = np.insert(r*np.cos(angles), 0, float(self.point.x))
        y = np.insert(r*np.sin(angles), 0, float(self.point.y))
        return np.vstack((x, y))

    @property
    def draw_coords(self) -> NDArray[Any]:
        angles = np.linspace(float(self.angle_start), float(self.angle_end))
        r = self.radius
        x = np.concatenate(((self.point.x,),
                            r*np.cos(angles),
                            (self.point.x,)))
        y = np.concatenate(((self.point.y,),
                            r*np.sin(angles),
                            (self.point.y,)))
        return np.vstack((x, y))


@dataclass(frozen=True)
class Segment:
    """
    Shape bounded by an arc of a circle centered at the origin and a
    line segment between the endpoints of the arc.

    Members:
        angle_start : the starting angle of the arc
        angle_end : the ending angle of the arc
        radius : the radius of the circle
    """
    angle_start: RealNumber
    angle_end: RealNumber
    radius: RealNumber = 1

    def rotate(self, angle: RealNumber, /) -> Self:
        angle_start = self.angle_start
        angle_end = self.angle_end
        angle_start += angle
        angle_end += angle
        if angle_start > angle_end:
            #angle_end += 2*mp.pi
            angle_start, angle_end = angle_end, angle_start

        return self.__class__(angle_start, angle_end, self.radius)

    @property
    def coords(self) -> NDArray[Any]:
        r = self.radius
        angles = np.linspace(float(self.angle_start), float(self.angle_end))
        return np.vstack((r*np.cos(angles), r*np.sin(angles)))

    @property
    def draw_coords(self) -> NDArray[Any]:
        r = self.radius
        angles = np.linspace(float(self.angle_start), float(self.angle_end))
        x = np.append(r*np.cos(angles), r*np.cos(float(self.angle_start)))
        y = np.append(r*np.sin(angles), r*np.sin(float(self.angle_start)))
        return np.vstack((x, y))


# used on the root triangle node only
@dataclass(frozen=True)
class RootTriangleShapeCollection:
    """
    All the relevant shapes on a root triangle node.
    
    Members:
        triangle: the actual root triangle
        a_segment : the segment on side a
        b_segment : the segment on side b
        c_segment : the segment on side c
    """

    triangle: Triangle
    a_segment: Segment
    b_segment: Segment
    c_segment: Segment

    @classmethod
    def from_triangle(cls, /, triangle: Triangle) -> Self:
        radius = triangle.a.dist()
        angle_a = triangle.a.angle
        angle_b = triangle.b.angle
        angle_c = triangle.c.angle
        a_segment = Segment(
            min(angle_b, angle_c), max(angle_b, angle_c), radius
        )
        b_segment = Segment(
            min(angle_a, angle_c), max(angle_a, angle_c), radius
        )
        c_segment = Segment(
            min(angle_a, angle_b), max(angle_a, angle_b), radius
        )
        return cls(triangle, a_segment, b_segment, c_segment)

    def rotate(self, angle: RealNumber, /) -> Self:
        return self.__class__(self.triangle.rotate(angle),
                              self.a_segment.rotate(angle),
                              self.b_segment.rotate(angle),
                              self.c_segment.rotate(angle))

# used on a root side node or a base triangle node
@dataclass(frozen=True)
class BaseTriangleShapeCollection:
    """
    All the relevant shapes on a base triangle node or root side node.
    
    Members:
        triangle : the base positive triangle in transformed space
                   a rotated version in untransformed space
        segment : the segment on the bottom of the base triangle
                  a rotated version in untransformed space
    """

    triangle: PositiveTriangle
    segment: Segment

    @classmethod
    def from_positive_triangle(
        cls, /, triangle: PositiveTriangle
    ) -> Self:
        radius = triangle.left.dist()
        segment = Segment(triangle.left.angle, triangle.right.angle, radius)
        return cls(triangle, segment)

    def rotate(self, angle: RealNumber, /) -> Self:
        return self.__class__(self.triangle.rotate(angle),
                              self.segment.rotate(angle))

# used on a base side node
@dataclass(frozen=True)
class BaseSideShapeCollection:
    """
    All the relevant shapes on a base side node. There is only one
    pseudo-sector here; this is purely for symmetry with other nodes.
    
    Members:
        pseudo_sector: the pseudo-sector to the left/right of a base
                       triangle in transformed space
                       a rotated version in untransformed space
    """

    pseudo_sector: PseudoSector

    @classmethod
    def from_positive_triangle_pair(
        cls, /,
        triangle: PositiveTriangle,
        above: PositiveTriangle,
        side_type: BaseSideType
    ) -> Self:
        radius = triangle.left.dist()
        if side_type == BaseSideType.LEFT:
            return cls(PseudoSector(
                triangle.top, above.left.angle, triangle.left.angle, radius
            ))
        elif side_type == BaseSideType.RIGHT:
            return cls(PseudoSector(
                triangle.top, triangle.right.angle, above.right.angle, radius
            ))

    def rotate(self, angle: RealNumber, /) -> Self:
        return self.__class__(self.pseudo_sector.rotate(angle))


# used on a normal triangle node
@dataclass(frozen=True)
class NormalTriangleShapeCollection:
    """
    All the relevant shapes on a normal triangle node.
    
    Members:
        triangle : the positive triangle in transformed space
                   a rotated version in untransformed space
        negative_triangle: the mirrored negative triangle in transformed
                           space
                           a rotated version in untransformed space
        horizontal_pseudo_sector: the horizontal pseudo-sector in transformed
                                  space
                                  a rotated version in untransformed space
        vertical_pseudo_sector: the vertical pseudo-sector in transformed space
                                a rotated version in untransformed space
    """

    triangle: PositiveTriangle
    negative_triangle: NegativeTriangle
    horizontal_pseudo_sector: PseudoSector
    vertical_pseudo_sector: PseudoSector

    @classmethod
    def from_positive_triangle_triplet(
        cls, /,
        triangle: PositiveTriangle,
        touching_horizontal: PositiveTriangle,
        touching_vertical: PositiveTriangle,
        side: BaseSideType,
    ) -> Self:


        radius = (triangle.left
                  if side == BaseSideType.LEFT else
                  triangle.right).dist()
        horizontal_angle_start = (touching_vertical.left
                                  if side == BaseSideType.LEFT else
                                  triangle.right).angle
        horizontal_angle_end = (triangle.left
                                if side == BaseSideType.LEFT else
                                touching_vertical.right).angle
        vertical_angle_start = (triangle.left
                                if side == BaseSideType.LEFT else
                                touching_horizontal.right).angle
        vertical_angle_end = (touching_horizontal.left
                              if side == BaseSideType.LEFT else
                              triangle.right).angle

        negative_triangle = NegativeTriangle.from_positive_triangle(
            triangle, side
        )

        horizontal_pseudo_sector = PseudoSector(
            triangle.top,
            horizontal_angle_start,
            horizontal_angle_end,
            radius,
        )

        vertical_pseudo_sector = PseudoSector(
            triangle.right if side == BaseSideType.LEFT else triangle.left,
            vertical_angle_start,
            vertical_angle_end,
            radius,
        )

        return cls(
            triangle, negative_triangle,
            horizontal_pseudo_sector, vertical_pseudo_sector
        )

    def rotate(self, angle: RealNumber, /) -> Self:
        return self.__class__(self.triangle.rotate(angle),
                              self.negative_triangle.rotate(angle),
                              self.horizontal_pseudo_sector.rotate(angle),
                              self.vertical_pseudo_sector.rotate(angle))
