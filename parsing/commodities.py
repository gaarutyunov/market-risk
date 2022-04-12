from pathlib import Path

import datatable as dt

from glob import glob

__COMMODITIES_FOLDER__ = Path("..", "data", "commodities")


def get_brent_history():
    """Получить данные по ежемесячным фьючерсам Brent

    Источник: https://iss.moex.com/iss/history/engines/futures/markets/forts/boards/RFUD/securities?from=2016-01-01&till=2022-01-01

    Информация по колонкам: https://iss.moex.com/iss/history/engines/futures/markets/forts/boards/RFUD/securities/columns

    :return: объект datatable
    """
    all_csvs = glob(str(__COMMODITIES_FOLDER__.joinpath("history", "*.csv")))
    df = dt.rbind(dt.iread(all_csvs))

    return df
