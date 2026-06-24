from dataclasses import dataclass
from typing import Self, override

from .types import IndexPart


@dataclass(frozen=True)
class Index:

    parts: tuple[IndexPart, ...]

    def __post_init__(self):
        if not self.parts:
            raise ValueError("The index must be nonempty.")

    def parent(self, /) -> Self:
        if len(self.parts) == 1:
            raise ValueError("The root triangle index does not have a parent.")
        return self.__class__(self.parts[:-1])
    
    def real_parent(self, /) -> Self:
        if len(self.parts) == 1:
            raise ValueError("The root triangle index does not have a parent.")

        if self.parts[-1] in (
            IndexPart.ROOT, IndexPart.BASE,
            IndexPart.NORMAL_HORIZONTAL, IndexPart.NORMAL_VERTICAL
        ):
            return self.__class__(self.parts[:-1])
        return self.__class__(self.parts[:-1]).parent()
    
    @override
    def __str__(self, /) -> str:
        return ''.join(
            'R' if part is IndexPart.ROOT else
            'a' if part is IndexPart.ROOT_SIDE_A else
            'b' if part is IndexPart.ROOT_SIDE_B else
            'c' if part is IndexPart.ROOT_SIDE_C else
            'B' if part is IndexPart.BASE else
            'l' if part is IndexPart.BASE_SIDE_LEFT else
            'r' if part is IndexPart.BASE_SIDE_RIGHT else
            'H' if part is IndexPart.NORMAL_HORIZONTAL else
            'V' if part is IndexPart.NORMAL_VERTICAL else
            '[unreachable]'
            for part in self.parts
        )

    @classmethod
    def root(cls):
        return cls((IndexPart.ROOT,))

    def root_side_a(self):
        if self.parts[-1] != IndexPart.ROOT:
            raise ValueError(
                "A root side part must be preceeded by a root part."
            )
        return self.__class__(self.parts + (IndexPart.ROOT_SIDE_A,))
    
    def root_side_b(self):
        if self.parts[-1] != IndexPart.ROOT:
            raise ValueError(
                "A root side part must be preceeded by a root part."
            )
        return self.__class__(self.parts + (IndexPart.ROOT_SIDE_B,))
    
    def root_side_c(self):
        if self.parts[-1] != IndexPart.ROOT:
            raise ValueError(
                "A root side part must be preceeded by a root part."
            )
        return self.__class__(self.parts + (IndexPart.ROOT_SIDE_C,))
    
    def base(self):
        if self.parts[-1] not in (
            IndexPart.ROOT_SIDE_A, IndexPart.ROOT_SIDE_B,
            IndexPart.ROOT_SIDE_C, IndexPart.BASE
        ):
            raise ValueError(
                "A base part must be preceeded "
                "by a base part or root side part"
            )
        return self.__class__(self.parts + (IndexPart.BASE,))

    def base_side_left(self):
        if self.parts[-1] is not IndexPart.BASE:
            raise ValueError(
                "A base side part must be preceeded by a base part."
            )
        return self.__class__(self.parts + (IndexPart.BASE_SIDE_LEFT,))
    
    def base_side_right(self):
        if self.parts[-1] is not IndexPart.BASE:
            raise ValueError(
                "A base side part must be preceeded by a base part."
            )
        return self.__class__(self.parts + (IndexPart.BASE_SIDE_RIGHT,))
    
    def normal_horizontal(self):
        if self.parts[-1] not in (
            IndexPart.BASE_SIDE_LEFT,
            IndexPart.BASE_SIDE_RIGHT,
            IndexPart.NORMAL_HORIZONTAL,
            IndexPart.NORMAL_VERTICAL
        ):
            raise ValueError(
                "A horizontal part must be preceeded "
                "by a base side part or a normal part."
            )
        return self.__class__(self.parts + (IndexPart.NORMAL_HORIZONTAL,))
    
    def normal_vertical(self):
        if self.parts[-1] not in (
            IndexPart.NORMAL_HORIZONTAL,
            IndexPart.NORMAL_VERTICAL
        ):
            raise ValueError(
                "A vertical part must be preceeded "
                "by a normal part."
            )
        return self.__class__(self.parts + (IndexPart.NORMAL_VERTICAL,))

    def get_attrgetter_string(self, /) -> str:
        return '.'.join(
            'root' if part is IndexPart.ROOT else
            'a' if part is IndexPart.ROOT_SIDE_A else
            'b' if part is IndexPart.ROOT_SIDE_B else
            'c' if part is IndexPart.ROOT_SIDE_C else
            'base' if part is IndexPart.BASE else
            'left' if part is IndexPart.BASE_SIDE_LEFT else
            'right' if part is IndexPart.BASE_SIDE_RIGHT else
            'horizontal' if part is IndexPart.NORMAL_HORIZONTAL else
            'vertical' if part is IndexPart.NORMAL_VERTICAL else
            '[unreachable]'
            for part in self.parts
        )
