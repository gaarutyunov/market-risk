from pathlib import Path
from typing import Optional, Iterable

import datatable as dt

from glob import glob

__STOCKS_FOLDER__ = Path("..", "data", "stocks")
__SELECTED_STOCKS__ = (
    "ALRS",
    "GAZP",
    "GMKN",
    "LKOH",
    "MGNT",
    "NLMK",
    "NVTK",
    "PLZL",
    "POLY",
    "ROSN",
)


def get_stocks_history(sec_ids: Optional[Iterable[str]] = __SELECTED_STOCKS__):
    """Получить данные по 10 акциям, входящим в индекс голубых фишек

    Состав индекса: https://www.moex.com/ru/index/MOEXBC/constituents/

    Источник: https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities?from=2016-01-01&till=2022-01-01

    Информация по колонкам: https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/columns

    :return: объект datatable
    """
    all_csvs = glob(str(__STOCKS_FOLDER__.joinpath("history", "*.csv")))
    df = dt.rbind(dt.iread(all_csvs))

    if sec_ids is None:
        return df

    return df[(dt.f.SECID == sec_id for sec_id in sec_ids), :]
