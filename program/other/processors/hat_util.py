import io
from typing import cast

import cairosvg  # pyright: ignore[reportMissingTypeStubs]
from mpmath import mp  # pyright: ignore[reportMissingTypeStubs]
from PIL import Image

from hell_sangaku.base.shapes import Point
from hell_sangaku.base.tree import BaseSideNode, RootSideNode, TriangleTree
from hell_sangaku.base.types import RealNumber


def attach_hats_to_image(
    tree: TriangleTree,
    image: Image.Image,
    location: str,
    *,
    figsize: float,
    dimension_scale: float,
    offset_x_scale: float,
    offset_y_scale: float
):
    for x in tree.walk():
        if isinstance(x, (RootSideNode, BaseSideNode)):
            continue
        A, B, C = [
            x.untransformed.triangle.a,
            x.untransformed.triangle.b,
            x.untransformed.triangle.c
        ]
        a, b, c = B.dist(C), A.dist(C), A.dist(B)
        try:
            incenter = (a*A + b*B + c*C)/(a + b + c)
        except ZeroDivisionError:
            continue
        inradius = cast(
            RealNumber,
            0.5 * mp.sqrt(  # pyright:ignore[reportUnknownMemberType]
                (b+c-a) * (c+a-b) * (a+b-c) / (a+b+c)
            )
        )

        hp = (a + b + c)/2
        area = cast(
            RealNumber,
            mp.sqrt(  # pyright:ignore[reportUnknownMemberType]
                hp * (hp - a) * (hp - b) * (hp - c)
            )
        )

        area_ratio = area / 4

        pixels = int(figsize*100)
        hat_image_area = area_ratio * pixels**2
        hat_image_dimension = int(cast(RealNumber,
            mp.sqrt(  # pyright:ignore[reportUnknownMemberType]
                hat_image_area
            ) * dimension_scale
        ))
        if hat_image_dimension <= 0:
            continue
        hat_png = io.BytesIO()
        try:
            # I HATE PEP 8, but i don't think I can do anything here
            _ = cairosvg.svg2png(  # pyright:ignore[reportUnknownMemberType, reportUnknownVariableType]
                url=location,
                output_width=hat_image_dimension,
                write_to=hat_png
            )
        except ValueError:
            continue
        hat_image = Image.open(hat_png)

        anchor = incenter

        # image space is a left-handed coordinate system
        anchor = Point(anchor.x, -anchor.y)

        anchor -= Point(0, inradius*0.8)

        # align (-1, -1) with (0, 0)
        anchor += Point(1, 1)

        anchor *= pixels//2

        anchor -= Point(
            offset_x_scale*hat_image_dimension,
            offset_y_scale*hat_image_dimension
        )

        anchor_coordinates = int(anchor.x), int(anchor.y)

        image.paste(hat_image, anchor_coordinates, hat_image)
