from pathlib import Path
from typing import Optional, Iterable, Union

import datatable as dt

from glob import glob

import numpy as np
import pandas as pd

__BONDS_FOLDER__ = Path("..", "data", "bonds")
__SELECTED__BONDS__ = (
    "SU26207RMFS9",
    "SU26209RMFS5",
    "SU26211RMFS1",
    "SU26212RMFS9",
    "SU26215RMFS2",
)

from parsing.base import Security


def get_bonds_history(sec_ids: Optional[Iterable[str]] = __SELECTED__BONDS__):
    """Получить данные по всем ОФЗ с фиксированным купоном (ОФЗ ПД)

    Источник: https://iss.moex.com/iss/history/engines/stock/markets/bonds/boards/TQOB/securities?from=2016-01-01&till=2022-01-01

    Информация по колонкам: https://iss.moex.com/iss/history/engines/stock/markets/bonds/boards/TQOB/securities/columns

    :return: объект datatable
    """
    all_csvs = glob(str(__BONDS_FOLDER__.joinpath("history", "*.csv")))
    df = dt.rbind(dt.iread(all_csvs))

    if sec_ids is None:
        return df

    return df[(dt.f.SECID == sec_id for sec_id in sec_ids), :]


def get_bonds_info(
    sec_ids: Optional[Iterable[str]] = __SELECTED__BONDS__,
) -> pd.DataFrame:
    """Получить информацию по ОФЗ ПД

    Источник: https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQOB/securities

    Информация по колонкам: https://iss.moex.com/iss/engines/stock/markets/bonds/boards/TQOB/securities/columns

    :return: :class:`pandas.DataFrame` с информациях по каждой ОФЗ"""
    df = pd.read_pickle(str(__BONDS_FOLDER__.joinpath("ofz_pd.pickle")))

    if sec_ids is None:
        return df

    return df.loc[df["SECID"].isin(pd.Series(sec_ids)).values, :]


def get_coupon_history(sec_ids: Optional[Iterable[str]] = __SELECTED__BONDS__):
    """Получить расписание выплаты купонов по ОФЗ с фиксированным купоном (ОФЗ ПД)

    Источник: https://iss.moex.com/iss/statistics/engines/stock/markets/bonds/bondization?from=2016-01-01&till=2022-01-01

    :return: объект datatable
    """
    all_csvs = glob(str(__BONDS_FOLDER__.joinpath("coupons", "*.csv")))
    df = dt.rbind(dt.iread(all_csvs))

    if sec_ids is None:
        return df

    return df[(dt.f.secid == sec_id for sec_id in sec_ids), :]


class Bond(Security):
    def __init__(self, sec_id: str) -> None:
        super().__init__('bonds', sec_id)
        self.info = get_bonds_info([sec_id])
        self.coupon_value = self.info[0, 'COUPONVALUE']

    @property
    def col_name(self) -> str:
        return 'bond_' + self.sec_id

    def returns(self, column: Union[str, list[str]] = "YIELDCLOSE", periods: int = 1) -> pd.Series:
        return self.history[column].diff(periods)

