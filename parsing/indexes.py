from pathlib import Path
from typing import Optional, Iterable

import datatable as dt

from glob import glob

__INDEX_FOLDER__ = Path("..", "data", "index")
__SELECTED_INDEXES__ = ("RTSI", "IMOEX")


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
