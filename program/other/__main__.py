#!/usr/bin/env python3
from __future__ import annotations

from PIL import Image

Image.MAX_IMAGE_PIXELS = None

from mpmath import mp  # pyright: ignore[reportMissingTypeStubs]

mp.prec = 100  # pyright: ignore[reportAttributeAccessIssue]

from .processor import Processor
from .processors.christmas import ChristmasProfilePicture
from .processors.halloween import HalloweenProfilePicture
from .processors.main import MainProfilePicture
from .processors.random import RandomExample

SETUPS: dict[str, Processor] = {
    'random': RandomExample(output="output/random.png"),
    'main': MainProfilePicture(output="output/main.png"),
    'main-alt': MainProfilePicture(output="output/main-alt.png", alt=True),
    'christmas': ChristmasProfilePicture(output="output/christmas.png"),
    'christmas-alt': ChristmasProfilePicture(
        output="output/christmas-alt.png", alt=True
    ),
    'halloween': HalloweenProfilePicture(output="output/halloween.png"),
    'halloween-alt': HalloweenProfilePicture(
        output="output/halloween-alt.png", alt=True
    ),
}


def main(setup: str) -> None:
    assert setup in SETUPS
    SETUPS[setup].process()

if __name__ == '__main__':
    possible_setups = ', '.join(SETUPS)
    while (setup := input(f"Choose ({possible_setups}): ")) not in SETUPS:
        pass
    main(setup)
