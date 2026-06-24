from collections.abc import Generator, Sequence

import numpy as np

from hell_sangaku.base.shapes import Point
from hell_sangaku.base.types import MPLColor


def is_mpl_color_transparent(color: MPLColor) -> bool:
    if color is None:
        return False
    if isinstance(color, str):
        return (color == 'none' or (color.startswith('#') and
                                    len(color) == 9 and
                                    color.endswith('00')))
    assert isinstance(color, tuple)
    if len(color) == 2:
        return color[1] == 0 or color[0] == 'none'
    if len(color) == 4:
        return color[3] == 0
    assert False


def is_mpl_color_opaque(color: MPLColor) -> bool:
    if color is None:
        return True
    if isinstance(color, str):
        return (color == 'none' or (color.startswith('#') and
                                    len(color) == 9 and
                                    color.lower().endswith('ff')))
    assert isinstance(color, tuple)
    if len(color) == 2:
        return color[1] == 1 and color[0] != 'none'
    if len(color) == 4:
        return color[3] == 1
    return True


def is_mpl_color_semitransparent(color: MPLColor) -> bool:
    return (
        not is_mpl_color_opaque(color) and not is_mpl_color_transparent(color)
    )

def _sliding_window[T](
    elements: Sequence[T],
    window_size: int
) -> Generator[list[T]]:

    elems = iter(elements)
    try:
        to_return: list[T] = [next(elems) for _ in range(window_size)]
    except StopIteration:
        # do not yield anything if there aren't enough elements
        # to complete the window
        return
    yield to_return
    while True:
        _ = to_return.pop(0)
        try:
            to_return.append(next(elems))
        except StopIteration:
            return
        yield to_return


def offset_polygon(points: Sequence[Point], dist: float, /) -> list[Point]:
    # this should work for all triangles, which is the only thing i
    # actually care about here, but it should work for polygons
    # generally, as long as the offset is sufficiently small compared to
    # the distance between the points, and the polygon is non-self
    # intersecting

    # when processing for example, a triangle ABC each point's offset
    # point is calculated based on the lines connecting them to the
    # previous and next point. the previous point of A should be C
    # and the next point of C should be A
    points = [points[-1], *points, points[0]]

    new_points: list[Point] = []
    for prev, curr, next in _sliding_window(points, 3):
        n1 = (prev - curr).rotate90().normalize()
        n2 = (curr - next).rotate90().normalize()
        bisector = (n1 + n2).normalize()
        length = dist / np.sqrt(0.5 + 0.5*n1.dot(n2))
        new_points.append(curr + length*bisector)
    return new_points
