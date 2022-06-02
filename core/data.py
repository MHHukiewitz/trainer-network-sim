from datetime import datetime, date
from typing import List, Any, Union, Optional
import pandas as pd
import numpy as np


class TimeSeries:
    df: pd.DataFrame
    freq: str

    def __init__(self, df: pd.DataFrame, freq="1D"):
        self.freq = freq
        self.df = df
        self.only_date = pd.to_timedelta(freq) >= pd.to_timedelta("1D")

    @property
    def datasets(self) -> [str]:
        return self.df.columns.to_list()

    @property
    def earliest(self) -> Optional[Union[date, datetime]]:
        earliest: Optional[datetime] = self.df.first_valid_index()
        if earliest:
            return earliest.date() if self.only_date else earliest
        return None

    @property
    def latest(self) -> Optional[Union[date, datetime]]:
        latest: Optional[datetime] = self.df.last_valid_index()
        if latest:
            return latest.date() if self.only_date else latest
        return None

    def add_observation(self):
        """Adds a new observation at the end of the dataframe for all columns."""
        date = self.latest + pd.to_timedelta(self.freq)
        self.fill(date, date)

    def fill(self,
             start: Union[datetime, str] = None,
             end: Union[datetime, str] = None,
             features: [str] = None):
        start = start if start else self.earliest
        end = end if end else self.latest
        features = features if features else self.df.columns
        self.df = self.get_extended_df(start, end)
        self.df.loc[start:end, features] = self.df.loc[start:end, features].add(1)

    def get_extended_df(self, start: Union[datetime, str] = None, end: Union[datetime, str] = None) -> pd.DataFrame:
        start = start if start < self.earliest else self.earliest
        end = end if end > self.latest else self.latest
        return self.df.reindex(pd.date_range(start=start, end=end, freq=self.freq), fill_value=0)

    def __add__(self, other) -> 'TimeSeries':
        self.check_other(other)
        other: TimeSeries
        return TimeSeries(self.df.add(other.df, fill_value=0), freq=self.freq)

    def check_other(self, other):
        if not isinstance(other, type(self)):
            raise Exception(f"{other} is not of type {type(self)}.")
        if not self.freq == other.freq:
            raise Exception(f"Frequencies do not match: self - {self.freq}, other - {other.freq}")

    def __copy__(self):
        return TimeSeries(self.df.copy(deep=True), self.freq)

    def __getitem__(self, item):
        return TimeSeries(pd.DataFrame(self.df[item]), self.freq)

    def __len__(self):
        return len(self.df)


def create_dataset(
        columns: List[str],
        empty: bool = False,
        start: Any = "2000-01-01",
        end: Any = "2000-03-01",
        freq="1D"):
    index = pd.date_range(start=start, end=end, freq=freq)
    data = None if empty else np.ones([len(index), len(columns)])
    df = pd.DataFrame(data=data, columns=columns, index=index, dtype=np.int8)
    return TimeSeries(df, freq)
