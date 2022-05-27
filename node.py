import hashlib
from typing import Optional

import numpy as np
from datetime import datetime

from numpy import datetime64

from data import TimeSeries


class Node:
    own_data: Optional[TimeSeries]
    received_data: Optional[TimeSeries]

    def __init__(self, own_data: TimeSeries = None):
        self.own_data = own_data
        self.received_data = None

    @property
    def name(self):
        return "0x" + hashlib.sha1(str(hash(self)).encode('ascii')).hexdigest()

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
            self.received_data = data

    def add_own_data(self, data: TimeSeries):
        if self.own_data:
            self.own_data = self.own_data + data
        else:
            self.own_data = data

    def tick(self):
        self.own_data.add_observations()

    def __str__(self):
        if self.own_data:
            own_data = f"Own data: {self.own_data.datasets} from {self.own_data.earliest} til {self.own_data.latest}"
        else:
            own_data = "No own data."
        if self.received_data:
            received_data = f"Received: {self.received_data.datasets} with earliest on {self.received_data.earliest} and latest on {self.received_data.latest}"
        else:
            received_data = "No received data."
        return f"Node [{self.name}] with\n  {own_data}\n  {received_data}"
