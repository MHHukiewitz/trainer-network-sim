import numpy as np

from typing import OrderedDict

from numpy import datetime64

from node import Node


class Network:
    nodes: OrderedDict[str, Node] = {}

    def add_node(self, node: Node):
        self.nodes[node.name] = node

    def tick(self):
        for node in self.nodes.values():
            node.tick()

    def print_nodes(self):
        for node in self.nodes.values():
            print(node)

    @property
    def earliest(self):
        array = [node.earliest for node in self.nodes.values()]
        return np.min(np.array(array, dtype=datetime64))

    @property
    def latest(self):
        return np.max(np.array([node.latest for node in self.nodes.values()], dtype=datetime64))

    def get_intervals(self):
        return
