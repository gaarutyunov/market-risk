import abc
from os import PathLike
from pathlib import Path
from typing import Callable, Union

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA

from metrics.var import calculate_garch, calculate, calculate_historical


class Security(abc.ABC):
    def __init__(self, folder: str, sec_id: str) -> None:
        self.folder = Path("..", "data", folder)
        self.sec_id = sec_id
        self._hist: pd.DataFrame = None
        self._pca: PCA = None

    @property
    def col_name(self) -> str:
        return self.sec_id

    @property
    def history_path(self) -> PathLike:
        return self.folder.joinpath("history", self.sec_id + ".csv")

    @property
    def history(self) -> pd.DataFrame:
        if self._hist is None:
            self._hist = self._history().sort_index()

        return self._hist

    def _history(self) -> pd.DataFrame:
        return pd.read_csv(
            self.history_path,
            index_col="TRADEDATE",
            parse_dates=["TRADEDATE"],
            header=0,
        )

    def returns(
        self, column: Union[str, list[str]] = "CLOSE", periods: int = 1
    ) -> pd.Series:
        return (
            self.history[column].replace(0, np.nan).dropna().pct_change(periods=periods)
        )

    def value_at_risk(
        self,
        periods: int = 1,
        alpha: float = 0.99,
        window_length: int = 252,
        calc_func: Callable[[pd.DataFrame, float], float] = calculate_garch,
        horizon: int = 1,
        **kwargs
    ) -> pd.Series:
        return calculate(self.returns(periods=periods, **kwargs), calc_func, window_length, alpha, horizon=horizon, **kwargs)

    def plot_value_at_risk(
        self,
        periods: int = 1,
        alpha: float = 0.99,
        window_length: int = 252,
        *args,
        **kwargs,
    ):
        self.returns(periods=periods, **kwargs).plot(
            label=kwargs.get("returns_label", "Доходность")
        )
        (
            -(
                self.value_at_risk(
                    periods,
                    alpha,
                    window_length,
                    calc_func=calculate_historical,
                    **kwargs
                )
            )
        ).plot(c="r", label="VaR (историческая симуляция)")
        (
            -(
                self.value_at_risk(
                    periods, alpha, window_length, calc_func=calculate_garch, **kwargs
                )
            )
        ).plot(c="g", label="VaR (GARCH)")
        plt.title(kwargs.get("title", "VaR " + self.sec_id))
        plt.ylabel(kwargs.get("ylabel", "Доходность"))
        plt.xlabel("Дата")
        plt.legend()
        plt.show()

    def pca(self, periods: int = 1, k: int = 3, **kwargs):
        if self._pca is None or self._pca.n_components != k:
            self._pca = PCA(n_components=k).fit(self.returns(periods=periods, **kwargs))

        return self._pca

    def pca_transform(
        self, periods: int = 1, k: int = 3, **kwargs
    ):
        pca = self.pca(periods, k, **kwargs)
        data = self.returns(periods=periods, **kwargs)
        return pca.transform(data)

    def plot_pca(
        self, periods: int = 1, k: int = 3, **kwargs
    ):
        pca = self.pca(periods, k, **kwargs)
        data = self.returns(periods=periods, **kwargs)
        plt.plot(data.columns, pca.components_.T)
        plt.legend([f"pc$_{i}(t)$" for i in range(1, k + 1)])
        plt.title(f"First {k} principal components")
        plt.show()
