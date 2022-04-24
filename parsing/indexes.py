from pathlib import Path
from typing import Optional, Iterable

import datatable as dt

from glob import glob

__INDEX_FOLDER__ = Path("..", "data", "index")
__SELECTED_INDEXES__ = ("RTSI", "IMOEX")

import pandas as pd

from parsing.base import Security


def get_indexes_history(sec_ids: Optional[Iterable[str]] = __SELECTED_INDEXES__):
    """Получить данные по индексам МосБиржи и РТС

    Источники:

    * https://iss.moex.com/iss/history/engines/stock/markets/index/boards/SNDX/securities/IMOEX?from=2016-01-01&till=2022-01-01
    * https://iss.moex.com/iss/history/engines/stock/markets/index/boards/RTSI/securities/RTSI?from=2016-01-01&till=2022-01-01

    Информация по колонкам:
    * https://iss.moex.com/iss/history/engines/stock/markets/index/boards/SNDX/securities/columns
    * https://iss.moex.com/iss/history/engines/stock/markets/index/boards/RTSI/securities/columns

    :return: объект datatable
    """
    all_csvs = glob(str(__INDEX_FOLDER__.joinpath("history", "*.csv")))
    df = dt.rbind(dt.iread(all_csvs))

    if sec_ids is None:
        return df

    return df[(dt.f.SECID == sec_id for sec_id in sec_ids), :]


def get_index_returns(prices, sec_id: str, periods: int = 1) -> pd.DataFrame:
    """Получить доходность по индексу в формате датафрейма"""
    df: pd.DataFrame = prices[dt.f.SECID == sec_id, ["TRADEDATE", "CLOSE"]].to_pandas()
    df.set_index(keys=["TRADEDATE"], inplace=True)

    return df.pct_change(periods=periods).sort_index()


class Index(Security):
    def __init__(self, sec_id: str) -> None:
        super().__init__("index", sec_id)

    @property
    def col_name(self) -> str:
        return "idx_" + self.sec_id
