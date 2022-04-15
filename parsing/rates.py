from pathlib import Path

import pandas as pd


__CREDIT_RATE_PATH__ = Path("..", "data", "credit_rate.csv")


def get_credit_rates() -> pd.DataFrame:
    """Возвращает информацию по ключевой ставке Банка России с 2016 по 2022 гг.

    Источник: https://www.cbr.ru/hd_base/KeyRate/?UniDbQuery.Posted=True&UniDbQuery.From=01.01.2016&UniDbQuery.To=01.01.2022

    :return: :class:`pandas.DataFrame` с ключевой ставкой
    """
    return pd.read_csv(
        str(__CREDIT_RATE_PATH__),
        delimiter="\t",
        header=None,
        names=["rate"],
        index_col=0,
        parse_dates=[0],
        dtype=float,
        decimal=",",
    )
