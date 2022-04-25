import abc
from os import PathLike
from pathlib import Path
from typing import Callable, Union

import numpy as np
import pandas as pd
import scipy.stats as ss
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA

from metrics.var import calculate_garch, calculate as calculate_var
from metrics.es import calculate


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
            return_kwargs=None,
            **kwargs
    ) -> pd.Series:
        if return_kwargs is None:
            return_kwargs = {}
        return calculate_var(self.returns(periods=periods, **return_kwargs), calc_func, window_length, alpha, horizon=horizon,
                             **kwargs)

    def expected_shortfall(self, periods: int = 1,
                           alpha: float = 0.975,
                           window_length: int = 252,
                           calc_func: Callable[[pd.DataFrame, float], float] = calculate_garch,
                           horizon: int = 1,
                           return_kwargs=None,
                           **kwargs):
        if return_kwargs is None:
            return_kwargs = {}
        return calculate(self.returns(periods=periods, **return_kwargs), calc_func, window_length, alpha, horizon=horizon,
                             **kwargs)

    def plot_returns(self,
                     periods: int = 1,
                     return_kwargs=None,
                     **kwargs):
        if return_kwargs is None:
            return_kwargs = {}
        self.returns(periods=periods, **return_kwargs).plot(
            label=kwargs.get("returns_label", "Доходность")
        )

    def plot_value_at_risk(
            self,
            periods: int = 1,
            alpha: float = 0.99,
            window_length: int = 252,
            calc_func: Callable[[pd.DataFrame, float], float] = calculate_garch,
            return_kwargs=None,
            plot_kwargs=None,
            *args,
            **kwargs,
    ):
        if plot_kwargs is None:
            plot_kwargs = {}
        if return_kwargs is None:
            return_kwargs = {}
        VaR = self.value_at_risk(
            periods, alpha, window_length, calc_func=calc_func, return_kwargs=return_kwargs, **kwargs
        )
        (-VaR).plot(c=plot_kwargs.get('color', 'g'), label=plot_kwargs.get('var_title', 'VaR'))
        plt.title(plot_kwargs.get("title", "VaR " + self.sec_id))
        plt.ylabel(plot_kwargs.get("ylabel", "Доходность"))
        plt.xlabel("Дата")
        plt.legend()

        return VaR

    def plot_expected_shortfall(
            self,
            periods: int = 1,
            alpha: float = 0.99,
            window_length: int = 252,
            calc_func: Callable[[pd.DataFrame, float], float] = calculate_garch,
            return_kwargs=None,
            plot_kwargs=None,
            **kwargs,
    ):
        ES = self.expected_shortfall(
            periods, alpha, window_length, calc_func=calc_func, return_kwargs=return_kwargs, **kwargs
        )
        ES.plot(c=plot_kwargs.get('color', 'g'), label=plot_kwargs.get('es_title', 'ES'))
        plt.title(plot_kwargs.get("title", "ES " + self.sec_id))
        plt.ylabel(plot_kwargs.get("ylabel", "Доходность"))
        plt.xlabel("Дата")
        plt.legend()

        return ES

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

    def backtest(self, metric: pd.Series, metric_label: str, alpha: float = .99) -> pd.DataFrame:
        returns: pd.Series = self.returns()
        hits: pd.Series = returns[metric.index] < -metric
        hit_times = hits.index[hits]
        returns.plot(label='Доходность')
        (-metric).plot(color='y', label=metric_label)
        plt.plot(hit_times, returns[hit_times], 'r*')
        plt.title("Пробои")
        plt.ylabel('Доходность')
        plt.xlabel('Даты')
        plt.legend()
        results_df = pd.DataFrame(columns=['Показатель', 'Значение'], dtype=object).set_index('Показатель')
        N = hits.size
        n = hits.sum()
        results_df.loc['Доля пробоев, %'] = ['%.2f' % (n / N * 100)]
        p_val_greater = ss.binom_test(n, N, 1-alpha, alternative="greater")
        results_df.loc['P-value (greater), %'] = ['%.2f' % (p_val_greater * 100)]
        zn = zone(p_val_greater)
        results_df.loc['Зона светофора'] = [zn]

        return results_df


def zone(p):
    if p > 0.05:
        return "Зеленая"
    elif p > 0.0001:
        return "Желтая"
    else:
        return "Красная"