from enum import Enum
from typing import OrderedDict, Union, Dict, List, Set, Tuple, Optional

import numpy as np
import pandas as pd
from numpy import datetime64
from datetime import datetime, date, timedelta

from .config import config
from .data import DailySeries, create_daily_series
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
    start_date: date
    current_date: date
    owner_lookup: Dict[str, Node]
    tree_type: TreeType

    _tree: Optional[IntervalTreeNode]

    def __init__(self,
                 start_date: Union[str, datetime64, datetime, date] = datetime.now(),
                 current_date: Union[str, datetime64, datetime, date] = None,
                 tree_type: TreeType = TreeType.balanced_ltor):
        self.start_date = pd.to_datetime(start_date).date()
        self.current_date = pd.to_datetime(start_date).date() if current_date is None \
            else pd.to_datetime(current_date).date()
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
    def earliest(self) -> date:
        np_datetime = np.min(np.array([node.earliest for node in self.nodes.values()], dtype=datetime64))
        return pd.to_datetime(np_datetime).date()

    @property
    def latest(self) -> date:
        np_datetime = np.max(np.array([node.latest for node in self.nodes.values()], dtype=datetime64))
        np_datetime = pd.to_datetime(np_datetime).date()
        if np_datetime > self.current_date:
            return self.current_date
        else:
            return np_datetime

    def observations(self, dataset: str) -> np.ndarray:
        return np.array([node.observations(dataset) for node in self.nodes.values()])

    def add_node(self, node: Node):
        self.nodes[node.name] = node
        for dataset in node.own_data.columns:
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
                node.add_own_data(create_daily_series(columns=[f"{node.name}-{k + 1}"], start=data_start, end=data_end))
            nodes.append(node)
        self.add_nodes(nodes)
        return nodes

    def remove_node(self, node: str):
        del self.nodes[node]
        self.generate_tree()

    def tick(self):
        self.current_date += timedelta(1)
        for node in self.nodes.values():
            node.tick(self.current_date)

    def get_intervals(self) -> Dict[str, Tuple[datetime, datetime]]:
        """Returns a datetime interval to be assigned to every node"""
        # TODO: Maybe distribute newer data more thinly than older data?
        intervals: (datetime, datetime) = {}
        date_range = pd.date_range(self.earliest, self.latest, len(self.nodes) + 1)
        for i, node in enumerate(self.tree.left_to_right):
            intervals[node.value] = (date_range[i], date_range[i + 1])
        return intervals

    def get_daily_series(self, dataset: str) -> Optional[DailySeries]:
        node = self.owner_lookup.get(dataset)
        if node:
            return node.own_data[dataset]
        return None

    def get_all_dataset_names(self) -> List[str]:
        return list(set(self.owner_lookup.keys()))

    def get_dataset_copies(self, dataset: str) -> pd.DataFrame:
        """Returns a DataFrame with the amount of copies of a single slice for all slices of given dataset"""
        df = next(iter(self.nodes.values())).received_data[dataset]
        empty = df.copy()
        empty.values[:] = 0
        for node in list(self.nodes.values())[1:]:
            if node.received_data is not None:
                df = pd.concat([df, node.received_data[dataset]], axis=1).fillna(0)
            else:
                df = pd.concat([df, empty], axis=1).fillna(0)
        df.applymap(lambda x: np.maximum(x, 1))
        df = df.div(df)
        df = df.fillna(0)
        return df.sum(axis=1)

    def distribute_series(self, dataset: str):
        """Distributes slices of a dataset"""
        timeseries = self.get_daily_series(dataset)
        for receiver, (start, end) in self.get_intervals().items():
            self.nodes[receiver].receive_data(timeseries[start:end])

    def allocate_dataframes(self, start: datetime, end: datetime):
        for node in self.nodes.values():
            node.received_data.extend_to_date(start, end, inplace=True)
            node.own_data.extend_to_date(start, end, inplace=True)

    def print_nodes(self):
        for node in self.nodes.values():
            print(node)

    def print_dataset_intervals(self, dataset: str):
        series = self.get_daily_series(dataset)
        intervals = self.get_intervals()
        print(f"Printing intervals of dataset {dataset}")
        for node in self.nodes.values():
            if node.received_data is not None:
                bar = ""
                received = node.received_data[dataset].reindex(
                    pd.date_range(start=series.earliest, end=series.latest, freq="1D"),
                    fill_value=0
                )
                for index in series.index:
                    if intervals[node.name][0] <= index <= intervals[node.name][1] and (received.loc[index] > 0).all():
                        bar += "█"
                    else:
                        bar += "▒" if (received.loc[index] > 0).all() else "-"
                print(f"[{series.earliest}]{bar}[{series.latest}] -> {node.name}")

    def print_dataset_distribution(self, dataset: str):
        data = self.get_daily_series(dataset)
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
        total = len(self.get_daily_series(dataset))
        print(f"Minimum amount of ticks observed: {obs.min(): .2f} of {total} ({100 * obs.min() / total: .1f} %)")
        print(f"Average amount of ticks observed: {obs.mean(): .2f} of {total} ({100 * obs.mean() / total: .1f} %)")
        print(f"Maximum amount of ticks observed: {obs.max(): .2f} of {total} ({100 * obs.max() / total: .1f} %)")


def create_network(nodes_cnt: int, days_of_data: int = None, tree_type: TreeType = TreeType.ordered_ltor) -> Network:
    today = datetime.now().date()
    if days_of_data is None:
        days_of_data = nodes_cnt
    net = Network(tree_type=tree_type, start_date=today + timedelta(days_of_data))
    net.create_nodes(nodes_cnt, 1, data_start=today, data_end=today + timedelta(days_of_data))
    return net
