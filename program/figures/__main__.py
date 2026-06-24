#!/usr/bin/env python3
from __future__ import annotations

from mpmath import mp  # pyright: ignore[reportMissingTypeStubs]

mp.prec = 100  # pyright: ignore[reportAttributeAccessIssue]

from .processor import Processor
from .processors.figure1 import Figure1
from .processors.figure2a import Figure2a
from .processors.figure2b import Figure2b
from .processors.figure3 import Figure3
from .processors.figure4 import Figure4
from .processors.figure5 import Figure5

SETUPS: dict[str, Processor] = {
    'figure1': Figure1(output="../document/figure1.svg"),
    'figure2a': Figure2a(output="../document/figure2a.svg"),
    'figure2b': Figure2b(output="../document/figure2b.svg"),
    'figure3': Figure3(output="../document/figure3.svg"),
    'figure4': Figure4(output="../document/figure4.svg"),
    'figure5': Figure5(output="../document/figure5.svg"),
}


def main(setup: str) -> None:
    assert setup in SETUPS
    SETUPS[setup].process()

if __name__ == '__main__':
    possible_setups = ', '.join(SETUPS)
    while (setup := input(f"Choose ({possible_setups}): ")) not in SETUPS:
        pass
    main(setup)
