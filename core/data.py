from datetime import datetime, date, timedelta
from typing import List, Any, Union, Optional
import pandas as pd
import numpy as np


class DailySeries(pd.DataFrame):
    @property
    def earliest(self) -> Optional[date]:
        earliest: Optional[datetime] = self.first_valid_index()
        if earliest:
            return earliest.date()
        return None

    @property
    def latest(self) -> Optional[date]:
        latest: Optional[datetime] = self.last_valid_index()
        if latest:
            return latest.date()
        return None

    def add_observation(self, day: date):
        """Adds a new observation at the end of the dataframe for all columns."""
        self._update_inplace(self.fill(day, day))

    def fill(self,
             start: Union[date, str] = None,
             end: Union[date, str] = None,
             features: [str] = None,
             inplace: bool = False) -> 'DailySeries':
        start = start if start else self.earliest
        end = end if end else self.latest
        features = features if features else self.columns
        df = self.extend_to_date(start, end)
        df.loc[start:end, features] = df.loc[start:end, features].add(1)
        if inplace:
            self._update_inplace(df)
        return df

    def extend_to_date(self,
                       start: Union[date, str] = None,
                       end: Union[date, str] = None,
                       inplace: bool = False) -> 'DailySeries':
        start = start if start < self.earliest else self.earliest
        end = end if end > self.latest else self.latest
        df = self.reindex(pd.date_range(start=start, end=end, freq="1D"), fill_value=0)
        if inplace:
            self._update_inplace(df)
        return df

    def __copy__(self, *args, **kwargs) -> 'DailySeries':
        return DailySeries(super().__copy__(*args, **kwargs))

    def __add__(self, other) -> 'DailySeries':
        return DailySeries(self.add(other, fill_value=0))

    def __getitem__(self, item):
        return DailySeries(super().__getitem__(item))


def create_daily_series(
        columns: List[str],
        empty: bool = False,
        start: Any = "2000-01-01",
        end: Any = "2000-03-01"):
    index = pd.date_range(start=start, end=end, freq="1D")
    data = None if empty else np.ones([len(index), len(columns)])
    return DailySeries(data=data, columns=columns, index=index, dtype=np.int8)
