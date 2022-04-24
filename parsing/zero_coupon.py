from typing import Union

import pandas as pd

from parsing.base import Security


def rename(col: str) -> str:
    return col[len("period_") :]


class ZeroCoupon(Security):
    """Кривая бескупонной доходности

    Источник: https://www.moex.com/ru/marketdata/indices/state/g-curve/archive/"""

    def __init__(self) -> None:
        super().__init__("zcyc", "zcyc")

    def _history(self) -> pd.DataFrame:
        df = (
            pd.read_csv(
                self.history_path,
                skiprows=2,
                delimiter=";",
                decimal=",",
                parse_dates=["tradedate"],
                index_col=["tradedate"],
                header=0,
            )
            .drop(columns=["tradetime"])
            .rename(
                lambda x: "rate_" + x[len("period_") :] if "period_" in x else x, axis=1
            )
            / 100
        )
        df.index.names = ["TRADEDATE"]

        return df[(df.index > "2016-01-01") & (df.index < "2022-01-01")]

    def returns(
        self, column: Union[str, list[str]] = None, periods: int = 1
    ) -> pd.DataFrame:
        if column is None:
            hist = self.history
        else:
            hist = self.history[column]
        return hist.diff(periods)
