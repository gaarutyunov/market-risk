from pathlib import Path
from typing import Union

import pandas as pd


__CREDIT_RATE_PATH__ = Path("..", "data", "rate", "history", "rate.csv")

from parsing.base import Security


def get_credit_rates() -> pd.DataFrame:
    """Возвращает информацию по ключевой ставке Банка России с 2016 по 2022 гг.

    Источник: https://www.cbr.ru/hd_base/KeyRate/?UniDbQuery.Posted=True&UniDbQuery.From=01.01.2016&UniDbQuery.To=01.01.2022

    :return: :class:`pandas.DataFrame` с ключевой ставкой
    """
    df = pd.read_csv(
        str(__CREDIT_RATE_PATH__),
        delimiter="\t",
        header=None,
        names=["rate"],
        index_col=0,
        parse_dates=[0],
        dtype=float,
        decimal=",",
    )
    df["rate"] = df["rate"].astype(float)
    df["rate"] = df["rate"] / 100

    return df.sort_index()


class CreditRate(Security):
    def __init__(self) -> None:
        super().__init__("rate", "rate")

    def _history(self) -> pd.DataFrame:
        return get_credit_rates()

    def returns(
        self, column: Union[str, list[str]] = "rate", periods: int = 1
    ) -> pd.Series:
        return self.history[column].diff(periods)
