from pathlib import Path
from typing import Optional, Iterable

import datatable as dt

from glob import glob

__CURRENCIES_FOLDER__ = Path("..", "data", "currencies")
__SELECTED__CURRENCIES__ = ("EUR_RUB__TOD", "USD000000TOD", "CNY000000TOD")

import pandas as pd

from parsing.base import Security


def get_currencies_history(sec_ids: Optional[Iterable[str]] = __SELECTED__CURRENCIES__):
    """Получить данные по выбранным валютам

    Источник: https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/CETS/securities?from=2016-01-01&till=2022-01-01

    Информация по колонкам: https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/CETS/securities/columns

    :return: объект datatable
    """
    all_csvs = glob(str(__CURRENCIES_FOLDER__.joinpath("history", "*.csv")))
    df = dt.rbind(dt.iread(all_csvs))

    if sec_ids is None:
        return df

    return df[(dt.f.SECID == sec_id for sec_id in sec_ids), :]


def get_currency_returns(prices, sec_id: str, periods: int = 1) -> pd.DataFrame:
    """Получить доходность по валюте в формате датафрейма"""
    df: pd.DataFrame = prices[dt.f.SECID == sec_id, ["TRADEDATE", "CLOSE"]].to_pandas()
    df.set_index(keys=["TRADEDATE"], inplace=True)

    return df.pct_change(periods=periods).sort_index()


class Currency(Security):
    def __init__(self, sec_id: str) -> None:
        super().__init__("currencies", sec_id)
