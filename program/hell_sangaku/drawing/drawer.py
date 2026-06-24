from __future__ import annotations

from abc import ABC, abstractmethod

from ..base.tree import (BaseSideNode, BaseTriangleNode, NormalTriangleNode,
                         RootSideNode, RootTriangleNode, TriangleTree,
                         TriangleTreeNode)


class Drawer(ABC):
    
    @abstractmethod
    def draw_node(
        self, node: (
            RootTriangleNode | RootSideNode | BaseTriangleNode |
            BaseSideNode | NormalTriangleNode
        ), /
    ) -> None:
        pass
    
    def draw_tree(self, tree: TriangleTree, /) -> None:
        if tree.root is None:
            return
        stack: list[TriangleTreeNode] = [tree.root]
        while stack:
            node = stack.pop()
            self.draw_node(node)
            match node:
                case RootTriangleNode():
                    if node.a is not None:
                        stack.append(node.a)
                    if node.b is not None:
                        stack.append(node.b)
                    if node.c is not None:
                        stack.append(node.c)
                case RootSideNode():
                    if node.base is not None:
                        stack.append(node.base)
                case BaseTriangleNode():
                    if node.left is not None:
                        stack.append(node.left)
                    if node.right is not None:
                        stack.append(node.right)
                    if node.base is not None:
                        stack.append(node.base)
                case BaseSideNode():
                    if node.horizontal is not None:
                        stack.append(node.horizontal)
                case NormalTriangleNode():
                    if node.horizontal is not None:
                        stack.append(node.horizontal)
                    if node.vertical is not None:
                        stack.append(node.vertical)
