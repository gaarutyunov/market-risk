from pathlib import Path

import pandas as pd


__CREDIT_RATE_PATH__ = Path("..", "data", "credit_rate.csv")

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
    def __init__(self, folder: str, sec_id: str) -> None:
        super().__init__(folder, sec_id)
