from typing import Optional

import numpy as np
from datetime import datetime, date

from .data import DailySeries
from .words import words


class Node:
    own_data: Optional[DailySeries]
    received_data: Optional[DailySeries]
    assigned_start: Optional[datetime]
    assigned_end: Optional[datetime]
    _name: str

    def __init__(self, own_data: DailySeries = None, name: str = None):
        self.own_data = own_data
        self.received_data = None
        self._name = name

    @property
    def name(self):
        return words[hash(self) % len(words)] if self._name is None else self._name

    @property
    def earliest(self):
        earliest = np.min(np.array([self.own_data.earliest if self.own_data is not None else datetime.max,
                                    self.received_data.earliest if self.received_data is not None else datetime.max],
                                   dtype='datetime64'))
        return earliest

    @property
    def latest(self):
        return np.max(np.array([self.own_data.latest if self.own_data is not None else datetime.min,
                                self.received_data.latest if self.received_data is not None else datetime.min],
                               dtype='datetime64'))

    def receive_data(self, data: DailySeries):
        if self.received_data is not None:
            self.received_data = self.received_data + data
        else:
            self.received_data = DailySeries(data.__copy__())

    def add_own_data(self, data: DailySeries):
        if self.own_data is not None:
            self.own_data = self.own_data + data
        else:
            self.own_data = data

    def remove_own_data(self, dataset: str):
        del self.own_data[dataset]

    def tick(self, day: date):
        self.own_data.add_observation(day)

    def observations(self, dataset: str) -> float:
        if self.received_data is None:
            return 0.0
        return self.received_data.agg(np.count_nonzero)[dataset]

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
