from datetime import date
from pathlib import Path

import datatable as dt

from glob import glob

__COMMODITIES_FOLDER__ = Path("..", "data", "commodities")

import pandas as pd

from parsing.base import Security


def get_brent_history():
    """Получить данные по ежемесячным фьючерсам Brent

    Источник: https://iss.moex.com/iss/history/engines/futures/markets/forts/boards/RFUD/securities?from=2016-01-01&till=2022-01-01

    Информация по колонкам: https://iss.moex.com/iss/history/engines/futures/markets/forts/boards/RFUD/securities/columns

    :return: объект datatable
    """
    all_csvs = glob(str(__COMMODITIES_FOLDER__.joinpath("history", "*.csv")))
    df = dt.rbind(dt.iread(all_csvs))

    return df


class Brent(Security):
    def __init__(self, period: int = 1) -> None:
        super().__init__("commodities", "brent")
        self.period = period

    def _history(self) -> pd.DataFrame:
        bh = get_brent_history()
        bh_grouped = bh[:, {"LASTDELDATE": dt.max(dt.f.TRADEDATE)}, dt.by("SECID")]
        shifted = (
            bh_grouped[:, :, dt.sort("LASTDELDATE")].to_pandas().shift(-self.period)
        )
        shifted["BUYDATE"] = shifted["LASTDELDATE"].shift(self.period)
        shifted.iloc[0, shifted.columns.get_loc("BUYDATE")] = "2016-01-04"
        result = shifted.dropna()
        result = result[result["BUYDATE"] < "2021-12-30"]

        concatenated = pd.DataFrame(columns=bh.names)

        for _, row in result.iterrows():
            lastdate = date(
                row["LASTDELDATE"].year,
                row["LASTDELDATE"].month,
                row["LASTDELDATE"].day,
            )
            buydate = date(
                row["BUYDATE"].year, row["BUYDATE"].month, row["BUYDATE"].day
            )
            filtered = bh[
                (dt.f.SECID == row["SECID"])
                & (dt.f.TRADEDATE < dt.Frame([lastdate]))
                & (dt.f.TRADEDATE >= dt.Frame([buydate])),
                :,
            ]
            concatenated = concatenated.append(filtered.to_pandas())

        return (
            concatenated.drop_duplicates(subset=["TRADEDATE"])
            .dropna()
            .set_index("TRADEDATE")
        )
