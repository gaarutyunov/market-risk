from pathlib import Path

import datatable as dt

from glob import glob

__BONDS_FOLDER__ = Path("..", "data", "bonds")


def get_bonds_history():
    """Получить данные по всем ОФЗ с фиксированным купоном (ОФЗ ПД)

    Источник: https://iss.moex.com/iss/history/engines/stock/markets/bonds/boards/TQOB/securities?from=2016-01-01&till=2022-01-01

    Информация по колонкам: https://iss.moex.com/iss/history/engines/stock/markets/bonds/boards/TQOB/securities/columns

    :return: объект datatable
    """
    return dt.fread(str(__BONDS_FOLDER__.joinpath("history.jay")))


if __name__ == "__main__":
    all_csvs = glob(str(__BONDS_FOLDER__.joinpath("history", "*.csv")))

    DT = dt.rbind(dt.iread(all_csvs))

    DT.to_jay(str(__BONDS_FOLDER__.joinpath("history.jay")))
