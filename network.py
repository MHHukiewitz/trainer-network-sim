from typing import OrderedDict, Union
import numpy as np
import pandas as pd
from numpy import datetime64
from datetime import datetime, date

from node import Node
from tree import IntervalTreeNode, build


class Network:
    nodes: OrderedDict[str, Node] = OrderedDict[str, Node]()
    current_date: datetime

    def __init__(self, current_date: Union[str, datetime64, datetime, date] = datetime.now()):
        self.current_date = pd.to_datetime(current_date)

    @property
    def tree(self) -> IntervalTreeNode:
        return build(self.nodes.keys())

    def add_node(self, node: Node):
        self.nodes[node.name] = node

    def add_nodes(self, nodes: [Node]):
        for node in nodes:
            self.add_node(node)
        self.refresh_intervals()

    def refresh_intervals(self):
        pd.date_range(self.earliest, self.latest, len(self.nodes))

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

    def get_interval(self) -> OrderedDict[datetime, Node]:
        intervals = []
        pd.date_range(self.earliest, self.latest, len(self.nodes))
        for i, node in enumerate(self.nodes.values()):
            node.assign_interval()
        return intervals
