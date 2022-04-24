import abc
from os import PathLike
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from metrics.var import calculate_garch, calculate, calculate_historical


class Security(abc.ABC):
    def __init__(self, folder: str, sec_id: str) -> None:
        self.folder = Path("..", "data", folder)
        self.sec_id = sec_id
        self._hist = None

    @property
    def history_path(self) -> PathLike:
        return self.folder.joinpath("history", self.sec_id + ".csv")

    @property
    def history(self) -> pd.DataFrame:
        if self._hist is None:
            self._hist = self._history()

        return self._hist

    def _history(self) -> pd.DataFrame:
        return pd.read_csv(
            self.history_path,
            index_col="TRADEDATE",
            parse_dates=["TRADEDATE"],
            header=0,
        )

    def returns(self, column: str = "CLOSE", periods: int = 1) -> pd.Series:
        return (
            self.history[column]
            .replace(0, np.nan)
            .dropna()
            .pct_change(periods=periods)
            .sort_index()
        )

    def value_at_risk(
        self,
        column: str = "CLOSE",
        periods: int = 1,
        alpha: float = 0.99,
        window_length: int = 252,
        calc_func: Callable[[pd.DataFrame, float], float] = calculate_garch,
    ) -> pd.Series:
        return calculate(self.returns(column, periods), calc_func, window_length, alpha)

    def plot_value_at_risk(
        self,
        column: str = "CLOSE",
        periods: int = 1,
        alpha: float = 0.99,
        window_length: int = 252,
        **kwargs
    ):
        self.returns(column, periods).plot(
            label=kwargs.get("returns_label", "Доходность")
        )
        (
            -(
                self.value_at_risk(
                    column,
                    periods,
                    alpha,
                    window_length,
                    calc_func=calculate_historical,
                )
            )
        ).plot(c="r", label="VaR (историческая симуляция)")
        (
            -(
                self.value_at_risk(
                    column, periods, alpha, window_length, calc_func=calculate_garch
                )
            )
        ).plot(c="g", label="VaR (GARCH)")
        plt.title(kwargs.get("title", "VaR " + self.sec_id))
        plt.ylabel(kwargs.get("ylabel", "Доходность"))
        plt.xlabel("Дата")
        plt.legend()
        plt.show()
