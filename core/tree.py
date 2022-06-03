import random
from typing import List, Optional

from binarytree import Node as TreeNode, NodeValue, NodeNotFoundError, _ATTR_LEFT, _ATTR_RIGHT, NodeValueList


class IntervalTreeNode(TreeNode):
    parent: Optional["IntervalTreeNode"]

    def __init__(self,
                 value: NodeValue,
                 left: Optional["IntervalTreeNode"] = None,
                 right: Optional["IntervalTreeNode"] = None,
                 parent: Optional["IntervalTreeNode"] = None):
        super().__init__(value, left, right)
        self.parent = parent

    @property
    def leftmost(self) -> "IntervalTreeNode":
        node = self
        while node.left is not None:
            node = node.left
        return node

    @property
    def rightmost(self) -> "IntervalTreeNode":
        node = self
        while node.right is not None:
            node = node.right
        return node

    @property
    def left_to_right(self) -> List["IntervalTreeNode"]:
        """Returns a list representation by traversing the deepest nodes first and beginning on the deepest,
        left-most leaf. """
        nodes: List["IntervalTreeNode"] = [self.leftmost]
        current = nodes[0]
        if current.right:
            nodes.extend(current.right.left_to_right)
        while current.parent:
            if current.parent.left == current:
                nodes.append(current.parent)
                current = nodes[-1]
                if current.right:
                    nodes.extend(current.right.left_to_right)
            else:
                break
        return nodes


def build_ordered(values: NodeValueList, direction: str = "ltor") -> Optional[IntervalTreeNode]:
    nodes = [None if v is None else IntervalTreeNode(v) for v in values]

    for index in range(1, len(nodes)):
        node = nodes[index]
        if node is not None:
            parent_index = (index - 1) // 2
            parent = nodes[parent_index]
            if parent is None:
                raise NodeNotFoundError(
                    "parent node missing at index {}".format(parent_index)
                )
            if direction == "ltor":
                setattr(parent, _ATTR_LEFT if index % 2 else _ATTR_RIGHT, node)
            else:
                setattr(parent, _ATTR_RIGHT if index % 2 else _ATTR_LEFT, node)
            node.parent = parent

    return nodes[0] if nodes else None


# TODO: Keep tree position of existing nodes, do not reorganize
def build_balanced(values: NodeValueList, direction: str = "ltor") -> Optional[IntervalTreeNode]:
    nodes = [None if v is None else IntervalTreeNode(v) for v in values]
    root = nodes[0]
    for i in range(1, len(nodes)):
        node = nodes[i]
        if node is not None:
            parent = find_shallowest_branch(root, direction)
            if direction == "random":
                direction = random.choice(["ltor", "rtol"])
            if direction == "ltor":
                setattr(parent, _ATTR_LEFT if parent.left is None else _ATTR_RIGHT, node)
            else:
                setattr(parent, _ATTR_RIGHT if parent.right is None else _ATTR_LEFT, node)
            node.parent = parent

    return nodes[0] if nodes else None


def find_shallowest_branch(node: IntervalTreeNode, direction: str = "ltor") -> IntervalTreeNode:
    while node.leaf_count >= 2:
        if len(node.left.values) == len(node.right.values):
            if direction == "ltor":
                node = node.left
            else:
                node = node.right
        elif len(node.left.values) > len(node.right.values):
            node = node.right
        else:
            node = node.left
    return node
