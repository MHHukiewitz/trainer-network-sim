from typing import OrderedDict

from node import Node

class NodesDict(OrderedDict):
    def __getitem__(self, item) -> Node:
        return super(self).__getitem__(item)

    def __setitem__(self, key, value: Node):
        return super(NodesDict, self).__setitem__(key, value)


class Network:
    nodes: NodesDict = {}

    def add_node(self, node: Node):
        self.nodes[node.name] = node

    def tick(self):
        for node in self.nodes.values():
            node.tick()

    def print_nodes(self):
        for node in self.nodes.values():
            print(node)
