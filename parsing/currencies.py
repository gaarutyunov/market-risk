from pathlib import Path
from typing import Optional, Iterable

import datatable as dt

from glob import glob

__CURRENCIES_FOLDER__ = Path("..", "data", "currencies")
__SELECTED__CURRENCIES__ = ("EUR_RUB__TOD", "USD000000TOD", "HKDRUB_TOD")


def get_currencies_history(sec_ids: Optional[Iterable[str]] = __SELECTED__CURRENCIES__):
    """Получить данные по выбранным валютам

    Источник: https://iss.moex.com/iss/engines/currency/markets/selt/boards/CETS/securities?from=2016-01-01&till=2022-01-01

    Информация по колонкам: https://iss.moex.com/iss/history/engines/currency/markets/selt/boards/CETS/securities/columns

    :return: объект datatable
    """
    all_csvs = glob(str(__CURRENCIES_FOLDER__.joinpath("history", "*.csv")))
    df = dt.rbind(dt.iread(all_csvs))

    if sec_ids is None:
        return df

    return df[(dt.f.SECID == sec_id for sec_id in sec_ids), :]
