from pathlib import Path

import datatable as dt

from glob import glob

__BONDS_FOLDER__ = Path("..", "data", "bonds")

if __name__ == "__main__":
    all_csvs = glob(str(__BONDS_FOLDER__.joinpath("history", "*.csv")))

    DT = dt.rbind(dt.iread(all_csvs))

    DT.to_jay(str(__BONDS_FOLDER__.joinpath("history.jay")))
