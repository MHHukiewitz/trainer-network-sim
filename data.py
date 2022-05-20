from datetime import datetime
from typing import List, Any, Union, Optional
import pandas as pd
import dask


class Dataset:
    features: pd.DataFrame
    _freq: str

    def __init__(self,
                 features: pd.DataFrame,
                 freq="1h"):
        self._freq = freq
        self.features = features

    @property
    def earliest(self) -> Optional[datetime]:
        return self.features.first_valid_index()

    @property
    def latest(self) -> Optional[datetime]:
        return self.features.last_valid_index()

    def fill(self,
             features: [str],
             start: Union[datetime, str] = None,
             end: Union[datetime, str] = None,
             empty: bool = False):
        """
        fills an interval with given features
        :param features:
        :param start:
        :param end:
        :param empty:
        :return:
        """
        if start is None:
            start = self.earliest
        elif start < self.earliest:
            self.extend(start, before=True, empty=empty)
        if end is None:
            end = self.latest
        elif end > self.latest:
            self.extend(end, before=False, empty=empty)
        self.features.loc[start:end][features] = None if empty else True

    def extend(self, to: datetime, before=False, empty=False):
        if before:
            ix = pd.date_range(start=to, end=self.features.last(1).index, freq=self._freq)
        else:
            ix = pd.date_range(start=self.features.first(1).index, end=to, freq=self._freq)
        self.features.reindex(ix, fill_value=None if empty else True)

    def __add__(self, other):
        if not isinstance(other, type(self)):
            raise Exception(f"{other} is not of type Dataset.")
        if not self._freq == other._freq:
            raise Exception(f"Frequencies do not match: self - {self._freq}, other - {other._freq}")
        return Dataset(self.features.merge(other.features, sort=True), self._freq)

    def __copy__(self):
        return Dataset(self.features.copy(deep=True), self._freq)

    def __getitem__(self, item):
        return Dataset(self.features.loc[item], self._freq)


def create_dataset(
        features: List[str],
        empty: bool = True,
        start: Any = "2000-01-01",
        end: Any = "2000-01-31",
        freq="1h"):
    dtypes = {f: bool for f in features}
    features = dask.datasets.timeseries(start, end, freq, "1Y", dtypes)
    features.replace(value=None if empty else True, inplace=True)
    return Dataset(features, freq)
