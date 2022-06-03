from enum import Enum
from typing import OrderedDict, Union, Dict, List, Set, Tuple, Optional

import numpy as np
import pandas as pd
from numpy import datetime64
from datetime import datetime, date, timedelta

from .config import config
from .data import TimeSeries, create_dataset
from .node import Node
from .tree import IntervalTreeNode, build_ordered, build_balanced


class TreeType(Enum):
    ordered_rtol = 1  # breadth-first from right to left
    ordered_ltor = 2  # breadth-first from left to right
    balanced_rtol = 3  # shallowest branch first from right to left
    balanced_ltor = 4  # shallowest branch first from left to right
    balanced_random = 5  # shallowest branch first, randomly chosen direction


class Network:
    nodes_created: int = 0

    nodes: OrderedDict[str, Node]
    start_date: datetime
    owner_lookup: Dict[str, Node]
    tree_type: TreeType

    _tree: Optional[IntervalTreeNode]

    def __init__(self,
                 start_date: Union[str, datetime64, datetime, date] = datetime.now(),
                 tree_type: TreeType = TreeType.balanced_ltor):
        self.start_date = pd.to_datetime(start_date)
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

    def observations(self, dataset: str) -> np.ndarray:
        return np.array([node.observations(dataset) for node in self.nodes.values()])

    def add_node(self, node: Node):
        self.nodes[node.name] = node
        for dataset in node.own_data.df.columns:
            assert self.owner_lookup.get(dataset) is None
            self.owner_lookup[dataset] = node
        self.generate_tree()

    def add_nodes(self, nodes: [Node]):
        for node in nodes:
            self.add_node(node)

    def create_nodes(self,
                     nodes_cnt: int,
                     features_cnt: int,
                     data_start: Union[datetime, date, str] = None,
                     data_end: Union[datetime, date, str] = None) -> List[Node]:
        if data_start is None:
            data_start = self.start_date
        if data_end is None:
            data_end = self.latest
        nodes: List[Node] = []
        for i in range(nodes_cnt):
            if config["enumerate_nodes"]:
                node = Node(name=f"{self.nodes_created}")
                self.nodes_created += 1
            else:
                node = Node()
            for k in range(features_cnt):
                node.add_own_data(create_dataset(columns=[f"{node.name}-{k + 1}"], start=data_start, end=data_end))
            nodes.append(node)
        self.add_nodes(nodes)
        return nodes

    def remove_node(self, node: str):
        del self.nodes[node]
        self.generate_tree()

    def tick(self):
        for node in self.nodes.values():
            node.tick()

    def get_intervals(self) -> Dict[str, Tuple[datetime, datetime]]:
        """Returns a datetime interval to be assigned to every node"""
        # TODO: Maybe distribute newer data more thinly than older data?
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

    def get_dataset_copies(self, dataset: str) -> pd.DataFrame:
        df = next(iter(self.nodes.values())).received_data[dataset].df
        empty = df.copy()
        empty.values[:] = 0
        for node in list(self.nodes.values())[1:]:
            if node.received_data is not None:
                df = pd.concat([df, node.received_data[dataset].df], axis=1).fillna(0)
            else:
                df = pd.concat([df, empty], axis=1).fillna(0)
        df.applymap(lambda x: np.maximum(x, 1))
        df = df.div(df)
        df = df.fillna(0)
        return df.sum(axis=1)

    def distribute_dataset(self, dataset: str):
        """Distributes slices of a dataset"""
        data = self.get_dataset(dataset)
        for receiver, (start, end) in self.get_intervals().items():
            self.nodes[receiver].receive_data(data[start:end])

    def print_nodes(self):
        for node in self.nodes.values():
            print(node)

    def print_dataset_intervals(self, dataset: str):
        data = self.get_dataset(dataset)
        intervals = self.get_intervals()
        print(f"Printing intervals of dataset {dataset}")
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

    def print_dataset_distribution(self, dataset: str):
        data = self.get_dataset(dataset)
        df = self.get_dataset_copies(dataset)
        print(f"Printing distribution of dataset {dataset}")
        for depth in range(int(df.max()), 0, -1):
            bar = ""
            for index in df.index:
                if (depth <= df.loc[index]).all():
                    bar += "█"
                else:
                    bar += " "
            print(f"[{data.earliest}]{bar}[{data.latest}] -> {depth} copies")

    def print_statistics(self, dataset: str):
        obs = self.observations(dataset)
        total = len(self.get_dataset(dataset))
        print(f"Minimum amount of ticks observed: {obs.min(): .2f} of {total} ({100 * obs.min() / total: .1f} %)")
        print(f"Average amount of ticks observed: {obs.mean(): .2f} of {total} ({100 * obs.mean() / total: .1f} %)")
        print(f"Maximum amount of ticks observed: {obs.max(): .2f} of {total} ({100 * obs.max() / total: .1f} %)")


def create_network(nodes_cnt: int, days_of_data: int = None, tree_type: TreeType = TreeType.ordered_ltor) -> Network:
    today = datetime.now().date()
    if days_of_data is None:
        days_of_data = nodes_cnt
    net = Network(tree_type=tree_type, start_date=today)
    net.create_nodes(nodes_cnt, 1, data_start=today, data_end=today + timedelta(days_of_data))
    return net
