from typing import OrderedDict, Union, Dict, List, Set, Tuple, Optional
import numpy as np
import pandas as pd
from numpy import datetime64
from datetime import datetime, date

from data import TimeSeries
from node import Node
from tree import IntervalTreeNode, build


class Network:
    nodes: OrderedDict[str, Node] = OrderedDict[str, Node]()
    current_date: datetime
    owner_lookup: Dict[str, Node] = {}

    def __init__(self, current_date: Union[str, datetime64, datetime, date] = datetime.now()):
        self.current_date = pd.to_datetime(current_date)

    @property
    def tree(self) -> IntervalTreeNode:
        return build(self.nodes.keys())

    def add_node(self, node: Node):
        self.nodes[node.name] = node
        for dataset in node.own_data.df.columns:
            assert self.owner_lookup.get(dataset) is None
            self.owner_lookup[dataset] = node

    def add_nodes(self, nodes: [Node]):
        for node in nodes:
            self.add_node(node)

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

    def get_intervals(self) -> Dict[str, Tuple[datetime, datetime]]:
        """Returns a datetime interval to be assigned to every node"""
        intervals: (datetime, datetime) = {}
        date_range = pd.date_range(self.earliest, self.latest, len(self.nodes) + 1)
        for i, node in enumerate(self.tree.left_to_right):
            intervals[node.value] = (date_range[i], date_range[i+1])
        return intervals

    def get_dataset(self, dataset: str) -> Optional[TimeSeries]:
        node = self.owner_lookup.get(dataset)
        if node:
            return node.own_data[dataset]
        return None

    def get_all_dataset_names(self) -> List[str]:
        return list(set(self.owner_lookup.keys()))

    def distribute_dataset(self, dataset: str):
        """Distributes slices of a dataset"""
        data = self.get_dataset(dataset)
        for receiver, (start, end) in self.get_intervals().items():
            self.nodes[receiver].receive_data(data[start:end])
