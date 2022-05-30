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
        while current.parent:
            if current.parent.left == current:
                nodes.append(current.parent)
                current = nodes[-1]
                if current.right:
                    nodes.extend(current.right.left_to_right)
            else:
                break
        return nodes


#TODO: Build very balanced
def build_l_to_r(values: NodeValueList) -> Optional[IntervalTreeNode]:
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
            setattr(parent, _ATTR_LEFT if index % 2 else _ATTR_RIGHT, node)
            node.parent = parent

    return nodes[0] if nodes else None

def build_r_to_l(values: NodeValueList) -> Optional[IntervalTreeNode]:
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
            setattr(parent, _ATTR_RIGHT if index % 2 else _ATTR_LEFT, node)
            node.parent = parent

    return nodes[0] if nodes else None