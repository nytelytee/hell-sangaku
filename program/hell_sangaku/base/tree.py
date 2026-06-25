from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Self, cast, final

import mpmath  # pyright: ignore[reportMissingTypeStubs]
from mpmath import mp  # pyright: ignore[reportMissingTypeStubs]

from .index import Index
from .shapes import (BaseSideShapeCollection, BaseTriangleShapeCollection,
                     NormalTriangleShapeCollection, Point, PositiveTriangle,
                     RootTriangleShapeCollection, Triangle)
from .types import BaseSideType, NormalTriangleType, RealNumber, RootSideType


class Data(ABC):

    @classmethod
    @abstractmethod
    def create(cls, /, key: str, node: TriangleTreeNode) -> Self:
        raise NotImplementedError

@dataclass
class TriangleTree:
    """
    A type representing a tree, containing one root triangle node.

    Arbitrary data classes may be passed to the tree; as new nodes
    are calculated, the data class' methods are called according to the
    data interface, to calculate arbitrary data, such as colors.
    """
    
    radius: RealNumber
    # arbitrary user data class that follows the Data interface
    data_types: dict[str, type[Data]]
    angle_alpha: RealNumber
    angle_beta: RealNumber
    angle_gamma: RealNumber
    angle_theta: RealNumber
    root: RootTriangleNode | None

    def __init__(
        self,
        alpha: RealNumber, beta: RealNumber,
        theta: RealNumber = mp.pi/2,
        radius: RealNumber = 1,
        /,
        **data: type[Data],
    ) -> None:

        self.angle_alpha = mp.mpf(alpha)
        self.angle_beta = mp.mpf(beta)
        self.angle_gamma = mp.pi - self.angle_alpha - self.angle_beta
        self.radius = mp.mpf(radius)
        self.angle_theta = mp.mpf(theta)
        self.data_types = data
        self.root = None

    def calculate_root(self) -> RootTriangleNode:
        if self.root is not None:
            return self.root
        A = Point(self.radius, mp.mpf(0)).rotate(self.angle_theta)
        B = A.rotate(2*self.angle_gamma)
        C = A.rotate(-2*self.angle_beta)
        self.root = RootTriangleNode(self, Triangle(A, B, C))
        return self.root

    def walk(self) -> Generator[TriangleTreeNode]:
        if self.root is None:
            return
        queue: deque[TriangleTreeNode] = deque([self.root])
        while queue:
            node = queue.pop()
            yield node
            match node:
                case RootTriangleNode():
                    if node.a is not None:
                        queue.appendleft(node.a)
                    if node.b is not None:
                        queue.appendleft(node.b)
                    if node.c is not None:
                        queue.appendleft(node.c)
                case RootSideNode():
                    if node.base is not None:
                        queue.appendleft(node.base)
                case BaseTriangleNode():
                    if node.left is not None:
                        queue.appendleft(node.left)
                    if node.right is not None:
                        queue.appendleft(node.right)
                    if node.base is not None:
                        queue.appendleft(node.base)
                case BaseSideNode():
                    if node.horizontal is not None:
                        queue.append(node.horizontal)
                case NormalTriangleNode():
                    if node.horizontal is not None:
                        queue.appendleft(node.horizontal)
                    if node.vertical is not None:
                        queue.appendleft(node.vertical)
    
    def calculate_tree(
        self,
        max_triangles: int,
        max_base_triangle_levels: int
    ) -> None:
        max_bases = 3*max_base_triangle_levels
        processed = 0
        enqueued_bases = 0
        queue: deque[
            Callable[[], TriangleTreeNode]
        ] = deque([self.calculate_root])
        while processed < max_triangles:
            node = queue.pop()()
            match node:
                case RootTriangleNode():
                    processed += 1
                    queue.appendleft(node.calculate_a)
                    queue.appendleft(node.calculate_b)
                    queue.appendleft(node.calculate_c)
                case RootSideNode():
                    if enqueued_bases < max_bases:
                        queue.appendleft(node.calculate_base)
                        enqueued_bases += 1
                case BaseTriangleNode():
                    processed += 1
                    queue.appendleft(node.calculate_left)
                    queue.appendleft(node.calculate_right)
                    if enqueued_bases < max_bases:
                        queue.appendleft(node.calculate_base)
                        enqueued_bases += 1
                case BaseSideNode():
                    queue.append(node.calculate_horizontal)
                case NormalTriangleNode():
                    processed += 1
                    queue.appendleft(node.calculate_horizontal)
                    queue.appendleft(node.calculate_vertical)
        

@final
@dataclass
class RootTriangleNode:
    """
    The root triangle node. Contains root side nodes.
    """

    tree: TriangleTree
    index: Index
    untransformed: RootTriangleShapeCollection

    data: dict[str, Data]

    a: RootSideNode | None
    b: RootSideNode | None
    c: RootSideNode | None

    def __init__(
        self, /,
        tree: TriangleTree,
        triangle: Triangle
    ) -> None:
        self.tree = tree
        self.index = Index.root()
        self.untransformed = RootTriangleShapeCollection.from_triangle(
            triangle
        )
        self.a = None
        self.b = None
        self.c = None
        self.data = {
            key: tree.data_types[key].create(key, self)
            for key in tree.data_types
        }

    def calculate_a(self) -> RootSideNode:
        if self.a is not None:
            return self.a
        self.a = RootSideNode(self.tree, RootSideType.A, self)
        return self.a
    
    def calculate_b(self) -> RootSideNode:
        if self.b is not None:
            return self.b
        self.b = RootSideNode(self.tree, RootSideType.B, self)
        return self.b
    
    def calculate_c(self) -> RootSideNode:
        if self.c is not None:
            return self.c
        self.c = RootSideNode(self.tree, RootSideType.C, self)
        return self.c


@final
@dataclass
class RootSideNode:
    """
    Node representing a view transformation attached to a
    root triangle node. The root triangle acts as a base triangle in
    that view transformation.
    """
    
    tree: TriangleTree
    index: Index
    parent: RootTriangleNode
    base: BaseTriangleNode | None
    data: dict[str, Data]
    
    type: RootSideType
    transformed: BaseTriangleShapeCollection
    angle_lambda_v: RealNumber
    angle_rho_v: RealNumber
    angle_tau_v: RealNumber
    angle_theta_v: RealNumber
    ratio_k_v: RealNumber

    def __init__(
        self, tree: TriangleTree,
        type: RootSideType,
        parent: RootTriangleNode
    ) -> None:

        self.tree = tree
        self.index = (
            parent.index.root_side_a() if type is RootSideType.A else
            parent.index.root_side_b() if type is RootSideType.B else
            parent.index.root_side_c()
        )
        self.parent = parent
        # todo: maybe useless since the index holds this info?
        self.type = type
        self.angle_lambda_v = (
            tree.angle_beta
            if type is RootSideType.A else
            tree.angle_gamma
            if type is RootSideType.B else
            tree.angle_alpha
        )
        self.angle_rho_v = (
            tree.angle_gamma
            if type is RootSideType.A else
            tree.angle_alpha
            if type is RootSideType.B else
            tree.angle_beta
        )
        self.angle_tau_v = (
            tree.angle_alpha
            if type is RootSideType.A else
            tree.angle_beta
            if type is RootSideType.B else
            tree.angle_gamma
        )
        self.angle_theta_v = cast(
            RealNumber,

            tree.angle_beta - tree.angle_gamma + mp.pi/2 - tree.angle_theta
            if type is RootSideType.A else
            tree.angle_beta - mp.pi/2 - tree.angle_theta
            if type is RootSideType.B else
            3*mp.pi/2 - tree.angle_gamma - tree.angle_theta
        )
        self.ratio_k_v = (
            mpmath.cot(  # pyright: ignore[reportUnknownMemberType]
                self.angle_lambda_v
            ) + 
            mpmath.cot(  # pyright: ignore[reportUnknownMemberType]
                self.angle_rho_v
            )
        )
        rotated_triangle = parent.untransformed.triangle.rotate(
            self.angle_theta_v
        )
        positive_triangle = PositiveTriangle.from_triangle(
            rotated_triangle, type
        )
        self.transformed = BaseTriangleShapeCollection.from_positive_triangle(
            positive_triangle
        )
        self.base = None
        self.data = {
            key: tree.data_types[key].create(key, self)
            for key in tree.data_types
        }

    def calculate_base(self) -> BaseTriangleNode:
        if self.base is not None:
            return self.base
        self.base = BaseTriangleNode(self.tree, self)
        return self.base

@final
@dataclass
class BaseTriangleNode:
    """
    Node representing a base triangle.
    """
    
    tree: TriangleTree
    index: Index
    parent: RootSideNode | BaseTriangleNode
    base: BaseTriangleNode | None
    left: BaseSideNode | None
    right: BaseSideNode | None
    data: dict[str, Data]
    
    # immediate jump to the first root side node
    root_side: RootSideNode

    transformed: BaseTriangleShapeCollection
    untransformed: BaseTriangleShapeCollection

    def __init__(
        self, tree: TriangleTree,
        parent: BaseTriangleNode | RootSideNode
    ) -> None:

        self.tree = tree
        self.index = parent.index.base()
        self.parent = parent
        self.root_side = (
            parent.root_side
            if isinstance(parent, BaseTriangleNode) else
            parent
        )
        # math from the base triangle section of the document
        k = self.root_side.ratio_k_v
        parent_top_y = self.parent.transformed.triangle.top.y
        r = self.tree.radius
        s = cast(
            RealNumber,
            mpmath.cot(  # pyright: ignore[reportUnknownMemberType]
                self.root_side.angle_lambda_v
            )
        )
        top_y = cast(RealNumber, (
            k**2 * parent_top_y  -
            2*mp.sqrt(  # pyright: ignore[reportUnknownMemberType]
                r**2 * k**2  -  k**2 * parent_top_y**2  +  4 * r**2
            )
        ) / (k**2 + 4))

        left_right_y = cast(RealNumber, (
            k**2 * top_y  -
            2*mp.sqrt(  # pyright: ignore[reportUnknownMemberType]
                r**2 * k**2  -  k**2 * top_y**2  +  4 * r**2
            )
        ) / (k**2 + 4))

        right_x = cast(
            RealNumber,
            mp.sqrt(  # pyright: ignore[reportUnknownMemberType]
                r**2 - left_right_y**2
            )
        )
        left_x = -right_x
        top_x = s*(top_y - left_right_y) + left_x
        # math done

        positive_triangle = PositiveTriangle.from_top_left_right(
            Point(top_x, top_y), Point(left_x, left_right_y),
            Point(right_x, left_right_y), self.root_side.type
        )

        self.transformed = BaseTriangleShapeCollection.from_positive_triangle(
            positive_triangle
        )

        self.untransformed = self.transformed.rotate(
            -self.root_side.angle_theta_v
        )

        self.base = None
        self.left = None
        self.right = None

        self.data = {
            key: tree.data_types[key].create(key, self)
            for key in tree.data_types
        }

    def calculate_left(self) -> BaseSideNode:
        if self.left is not None:
            return self.left
        self.left = BaseSideNode(self.tree, self, BaseSideType.LEFT)
        return self.left

    def calculate_right(self) -> BaseSideNode:
        if self.right is not None:
            return self.right
        self.right = BaseSideNode(self.tree, self, BaseSideType.RIGHT)
        return self.right
        
    def calculate_base(self) -> BaseTriangleNode:
        if self.base is not None:
            return self.base
        self.base = BaseTriangleNode(self.tree, self)
        return self.base


@final
@dataclass
class BaseSideNode:
    """
    Node representing a side on a base triangle.
    """
    
    tree: TriangleTree
    index: Index
    parent: BaseTriangleNode
    horizontal: NormalTriangleNode | None
    data: dict[str, Data]

    slope_s_v_d: RealNumber
    
    type: BaseSideType
    
    # immediate jump to the first root side node
    root_side: RootSideNode

    transformed: BaseSideShapeCollection
    untransformed: BaseSideShapeCollection

    def __init__(
        self, tree: TriangleTree,
        parent: BaseTriangleNode,
        side_type: BaseSideType
    ) -> None:

        self.tree = tree
        self.index = (
            parent.index.base_side_left()
            if side_type is BaseSideType.LEFT else
            parent.index.base_side_right()
        )
        self.parent = parent
        self.type = side_type
        self.root_side = parent.root_side
        self.transformed = BaseSideShapeCollection.from_positive_triangle_pair(
            parent.transformed.triangle,
            parent.parent.transformed.triangle,
            side_type
        )
        self.untransformed = self.transformed.rotate(
            -self.root_side.angle_theta_v
        )
        self.slope_s_v_d = (
            mpmath.cot(  # pyright: ignore[reportUnknownMemberType]
                self.root_side.angle_lambda_v
            )
            if side_type is BaseSideType.LEFT else
            -mpmath.cot(  # pyright: ignore[reportUnknownMemberType]
                self.root_side.angle_rho_v
            )
        )
        self.horizontal = None
        self.data = {
            key: tree.data_types[key].create(key, self)
            for key in tree.data_types
        }

    def calculate_horizontal(self) -> NormalTriangleNode:
        if self.horizontal is not None:
            return self.horizontal
        self.horizontal = NormalTriangleNode(
            self.tree, self, NormalTriangleType.HORIZONTAL
        )
        return self.horizontal


@dataclass
class NormalTriangleNode:
    """
    Node representing a normal triangle.
    """
    
    tree: TriangleTree
    index: Index
    parent: NormalTriangleNode | BaseSideNode
    
    # root side node because that has the transformed triangle shape
    touching_vertical: NormalTriangleNode | BaseTriangleNode | RootSideNode
    touching_horizontal: NormalTriangleNode | BaseTriangleNode

    horizontal: NormalTriangleNode | None
    vertical: NormalTriangleNode | None
    data: dict[str, Data]

    type: NormalTriangleType
    
    # immediate jump to the first root side node
    root_side: RootSideNode
    # immediate jump to the first base side node
    base_side: BaseSideNode

    transformed: NormalTriangleShapeCollection
    untransformed: NormalTriangleShapeCollection

    def __init__(
        self, tree: TriangleTree,
        parent: NormalTriangleNode | BaseSideNode,
        normal_type: NormalTriangleType
    ) -> None:
        self.tree = tree
        self.index = (
            parent.index.normal_horizontal()
            if normal_type is NormalTriangleType.HORIZONTAL else
            parent.index.normal_vertical()
        )
        self.type = normal_type
        self.parent = parent
        self.root_side = parent.root_side
        self.base_side = (
            parent.base_side
            if isinstance(parent, NormalTriangleNode) else
            parent
        )

        real_parent = cast(
            BaseTriangleNode | NormalTriangleNode,
            (
                self.parent
                if not isinstance(parent, BaseSideNode) else
                self.parent.parent
            )
        )

        if normal_type is NormalTriangleType.HORIZONTAL:
            self.touching_horizontal = real_parent
            self.touching_vertical = (
                real_parent.touching_vertical
                if isinstance(real_parent, NormalTriangleNode) else
                real_parent.parent
            )
        else:
            self.touching_horizontal = (
                real_parent.touching_horizontal
                if isinstance(real_parent, NormalTriangleNode) else
                cast(BaseTriangleNode | NormalTriangleNode, real_parent.parent)
            )
            self.touching_vertical = real_parent

        # start of normal triangle math from the document
        if normal_type is NormalTriangleType.HORIZONTAL:
            o = real_parent.transformed.triangle.top
        elif self.base_side.type == BaseSideType.RIGHT:
            o = real_parent.transformed.triangle.left
        else:
            o = real_parent.transformed.triangle.right

        r = self.tree.radius
        s = self.base_side.slope_s_v_d
        delta = -1 if self.base_side.type == BaseSideType.LEFT else 1
        sigma = delta*self.base_side.slope_s_v_d - self.root_side.ratio_k_v
        phi_y = (
            sigma**2*o.y - delta*sigma*o.x -
            mp.sqrt(  # pyright: ignore[reportUnknownMemberType]
                r**2 * (sigma**2 + 1)  -  (delta*o.x - sigma*o.y)**2
            )
        ) / (sigma**2 + 1)
        phi_x = s*(phi_y - o.y) + o.x
        psi_y = phi_y
        psi_x = cast(
            RealNumber,
            delta*mp.sqrt(  # pyright: ignore[reportUnknownMemberType]
                r**2 - phi_y**2
            )
        )

        left = (
            Point(psi_x, psi_y)
            if self.base_side.type is BaseSideType.LEFT else
            Point(phi_x, phi_y)
        )
        right = (
            Point(phi_x, phi_y)
            if self.base_side.type is BaseSideType.LEFT else
            Point(psi_x, psi_y)
        )
        top_y = o.y
        
        s_l = cast(
            RealNumber,
            mpmath.cot(  # pyright: ignore[reportUnknownMemberType]
                self.root_side.angle_lambda_v
            )
        )
        top_x = s_l*(top_y - left.y) + left.x
        top = Point(top_x, top_y)
        # end of math
        positive_triangle = PositiveTriangle.from_top_left_right(
            top, left, right,
            self.root_side.type
        )
        self.transformed = (
            NormalTriangleShapeCollection.from_positive_triangle_triplet(
                positive_triangle,
                self.touching_horizontal.transformed.triangle,
                self.touching_vertical.transformed.triangle,
                self.base_side.type
            )
        )
        self.untransformed = self.transformed.rotate(
            -self.root_side.angle_theta_v
        )
        self.horizontal = None
        self.vertical = None
        self.data = {
            key: tree.data_types[key].create(key, self)
            for key in tree.data_types
        }

    def calculate_horizontal(self) -> NormalTriangleNode:
        if self.horizontal is not None:
            return self.horizontal
        self.horizontal = NormalTriangleNode(
            self.tree, self, NormalTriangleType.HORIZONTAL
        )
        return self.horizontal
    
    def calculate_vertical(self) -> NormalTriangleNode:
        if self.vertical is not None:
            return self.vertical
        self.vertical = NormalTriangleNode(
            self.tree, self, NormalTriangleType.VERTICAL
        )
        return self.vertical


type TriangleTreeNode = (
    RootTriangleNode | RootSideNode | BaseTriangleNode |
    BaseSideNode | NormalTriangleNode
)
type TriangleTreeRealNode = (
    RootTriangleNode | BaseTriangleNode | NormalTriangleNode
)

