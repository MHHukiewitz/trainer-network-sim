from enum import Enum
from typing import OrderedDict, Union, Dict, List, Set, Tuple, Optional

import numpy as np
import pandas as pd
from numpy import datetime64
from datetime import datetime, date

from data import TimeSeries
from node import Node
from tree import IntervalTreeNode, build_ordered, build_balanced


class TreeType(Enum):
    ordered_rtol = 1  # breadth-first from right to left
    ordered_ltor = 2  # breadth-first from left to right
    balanced_rtol = 3  # shallowest branch first from right to left
    balanced_ltor = 4  # shallowest branch first from left to right
    balanced_random = 5  # shallowest branch first, randomly chosen direction


class Network:
    nodes: OrderedDict[str, Node]
    current_date: datetime
    owner_lookup: Dict[str, Node]
    tree_type: TreeType
    _tree: Optional[IntervalTreeNode]

    def __init__(self,
                 current_date: Union[str, datetime64, datetime, date] = datetime.now(),
                 tree_type: TreeType = TreeType.balanced_ltor):
        self.current_date = pd.to_datetime(current_date)
        self.tree_type = tree_type
        self.nodes = OrderedDict[str, Node]()
        self.owner_lookup = {}

    def generate_tree(self):
        if self.tree_type == TreeType.ordered_rtol:
            self._tree = build_ordered(self.nodes.keys(), "rtol")
        elif self.tree_type == TreeType.ordered_ltor:
            self._tree = build_ordered(self.nodes.keys(), "ltor")
        elif self.tree_type == TreeType.balanced_rtol:
            self._tree = build_balanced(self.nodes.keys(), "rtol")
        elif self.tree_type == TreeType.balanced_ltor:
            self._tree = build_balanced(self.nodes.keys(), "ltor")
        elif self.tree_type == TreeType.balanced_random:
            self._tree = build_balanced(self.nodes.keys(), "random")  # TODO: Lock in previous choices

    @property
    def tree(self) -> IntervalTreeNode:
        if self._tree is None:
            self.generate_tree()
        return self._tree

    @property
    def earliest(self):
        array = [node.earliest for node in self.nodes.values()]
        return np.min(np.array(array, dtype=datetime64))

    @property
    def latest(self):
        return np.max(np.array([node.latest for node in self.nodes.values()], dtype=datetime64))

    def add_node(self, node: Node):
        self.nodes[node.name] = node
        for dataset in node.own_data.df.columns:
            assert self.owner_lookup.get(dataset) is None
            self.owner_lookup[dataset] = node
        self.generate_tree()

    def add_nodes(self, nodes: [Node]):
        for node in nodes:
            self.add_node(node)

    def remove_node(self, node: str):
        del self.nodes[node]

    def tick(self):
        for node in self.nodes.values():
            node.tick()

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

    def print_nodes(self):
        for node in self.nodes.values():
            print(node)

    def print_dataset_distribution(self, dataset: str):
        data = self.get_dataset(dataset)
        intervals = self.get_intervals()
        print(f"Printing distribution of dataset {dataset}")
        for node in self.nodes.values():
            if node.received_data is not None:
                bar = ""
                received = node.received_data[dataset].df.reindex(
                    pd.date_range(start=data.earliest, end=data.latest, freq=data.freq),
                    fill_value=0
                )
                for index in data.df.index:
                    if intervals[node.name][0] <= index <= intervals[node.name][1]:
                        bar += "█"
                    else:
                        bar += "▒" if (received.loc[index] > 0).all() else "-"
                print(f"[{data.earliest}]{bar}[{data.latest}] -> {node.name}")