from typing import Optional, List, Union

import numpy as np
from datetime import datetime

from data import TimeSeries, create_dataset
from words import words


class Node:
    own_data: Optional[TimeSeries]
    received_data: Optional[TimeSeries]
    assigned_start: Optional[datetime]
    assigned_end: Optional[datetime]

    def __init__(self, own_data: TimeSeries = None):
        self.own_data = own_data
        self.received_data = None

    @property
    def name(self):
        return words[hash(self) % len(words)]

    @property
    def freq(self):
        # For simplicity reasons, assert that freq is everywhere the same
        if self.own_data and self.received_data:
            assert self.own_data.freq == self.received_data.freq
        return self.own_data.freq

    @property
    def earliest(self):
        earliest = np.min(np.array([self.own_data.earliest if self.own_data else datetime.max,
                                    self.received_data.earliest if self.received_data else datetime.max],
                                   dtype='datetime64'))
        return earliest

    @property
    def latest(self):
        return np.max(np.array([self.own_data.latest if self.own_data else datetime.min,
                                self.received_data.latest if self.received_data else datetime.min],
                               dtype='datetime64'))

    def receive_data(self, data: TimeSeries):
        if self.received_data:
            self.received_data = self.received_data + data
        else:
            self.received_data = data.__copy__()

    def add_own_data(self, data: TimeSeries):
        if self.own_data:
            self.own_data = self.own_data + data
        else:
            self.own_data = data

    def remove_own_data(self, dataset: str):
        del self.own_data.df[dataset]

    def tick(self):
        self.own_data.add_observation()

    def __str__(self):
        if self.own_data is not None:
            own_data = f"Own data: {self.own_data.datasets} from {self.own_data.earliest} til {self.own_data.latest}"
        else:
            own_data = "No own data."
        if self.received_data is not None:
            received_data = f"Received: {self.received_data.datasets} with earliest on {self.received_data.earliest} and latest on {self.received_data.latest}"
        else:
            received_data = "No received data."
        return f"Node \"{self.name}\" with\n  {own_data}\n  {received_data}"


def random_nodes(nodes_cnt: int,
                 features_cnt: int,
                 start: Union[datetime, str] = "2000-01-01",
                 to: Union[datetime, str] = "2000-02-01") -> List[Node]:
    nodes: List[Node] = []
    for i in range(nodes_cnt):
        node = Node()
        for k in range(features_cnt):
            node.add_own_data(create_dataset(columns=[f"{node.name}-{k + 1}"], start=start, end=to))
        nodes.append(node)
    return nodes
