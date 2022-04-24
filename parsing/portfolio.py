from typing import Union, Iterable, Callable

import pandas as pd
from sklearn.decomposition import PCA
from statsmodels.formula.api import ols
from tqdm.auto import tqdm

from parsing.base import Security


class SecurityGroup(Security):
    """Группа бумаг в портфеле.
    Группировка используется для того, чтобы собрать все активы одного класса в одну группу,
    на которую действуют определенные факторы риска"""
    def __init__(
        self,
        name: str,
        securities: Iterable[Security],
        factors: Iterable[Security],
        train_size: float = .8,
        weight: float = 1. / 3.,
        initial_investment: float = 10_000_000.,
        periods: int = 1,
        n_components: int = 3
    ) -> None:
        super().__init__("group", name)
        self.n_components = n_components
        self.sensitivities = None
        self.periods = periods
        self.securities_df = pd.DataFrame()
        self.factors_df = pd.DataFrame()
        self.factors_pca = pd.DataFrame()
        self.securities = securities
        self.factors = factors
        self.weight = weight
        self.initial_investment = initial_investment
        self.train_size = train_size
        for security in securities:
            self.securities_df[security.col_name] = security.returns(periods=periods)
        self.coefs = pd.DataFrame()
        self.models = {}
        self.fitted_ = False
        self.pca_ = None
        for factor in factors:
            rets = factor.returns(periods=periods)
            if len(rets.shape) == 1:
                self.factors_df[factor.col_name] = rets
            else:
                for name, ret in rets.items():
                    self.factors_df[name] = ret
        self.factors_df.dropna(inplace=True)

    def fit(self):
        """Вычисляет значения коэффициентов для риск-факторов.
        В процессе так же вычисляет главные компоненты, использую PCA."""
        if self.fitted_:
            return

        data = self.securities_df.copy()

        self.pca_: PCA = PCA(n_components=self.n_components).fit(self.factors_df)
        self.factors_pca: pd.DataFrame = pd.DataFrame(data=self.pca_.transform(self.factors_df.dropna()), index=self.factors_df.index)

        for i in range(self.factors_pca.shape[1]):
            factor = self.factors_pca.iloc[:, i]
            data['risk_' + str(i)] = factor

        for security in self.securities:
            f = f'{security.col_name} ~ '
            for name in self.factors_pca.columns.values:
                f += 'risk_' + str(name)
                f += ' + '

            f += '1'
            model = ols(f, data).fit()
            self.models[security.sec_id] = model
            self.coefs[security.sec_id] = model.params

        self.fitted_ = True

    def returns(self, column: Union[str, list[str]] = "CLOSE", periods: int = 1) -> pd.Series:
        """Вычисляет доходность всей группы инструментов"""
        weights = self.compute_weights()
        factors = self.factors_pca @ weights

        return factors.sum(axis=1)

    def compute_weights(self):
        """Вычисляет веса для риск факторов на основе вычисленных
         заранее коэффициентов и веса каждого из инструментов в портфеле.
         Для простоты используется equally-weighted подход."""
        n_securities = self.securities_df.shape[1]
        initial_weights = self.weight / n_securities
        prev_date = self.securities_df.shift(-1)
        new_weights: pd.DataFrame = pd.DataFrame(initial_weights * (1 - prev_date), index=self.securities_df.index)

        self.sensitivities = new_weights @ self.coefs

        return self.sensitivities


class Portfolio(Security):
    """Риск-факторный портфель"""
    def __init__(
        self,
        name: str,
        factors: Iterable[Security],
        securities: Iterable[SecurityGroup],
        periods: int = 1,
    ) -> None:
        super().__init__("portfolio", name)
        self.periods = periods
        self.factors_df = pd.DataFrame()
        for factor in factors:
            rets = factor.returns(periods=periods)
            if len(rets.shape) == 1:
                self.factors_df[factor.col_name] = rets
            else:
                for name, ret in rets.items():
                    self.factors_df[name] = ret
        self.factors_df.dropna(inplace=True)
        self.security_groups = {}
        self.securities_df = pd.DataFrame()
        for sec_group in securities:
            self.security_groups[sec_group.sec_id] = sec_group
            for sec in sec_group.securities:
                self.securities_df[sec.col_name] = sec.returns(periods=periods)

    def fit(self):
        """Вычисляет коэффициенты для каждой из групп активов по заданным риск факторам"""
        for name, sec_group in (pbar := tqdm(self.security_groups.items())):
            pbar.set_description('Fitting group %s' % name)
            sec_group.fit()
            for _, model in sec_group.models.items():
                print(model.summary())

    def returns(
        self, column: Union[str, list[str]] = "CLOSE", periods: int = 1
    ) -> pd.DataFrame:
        """Вычисляет доходность по всему портфелю для заданных риск факторов"""
        returns_df = pd.DataFrame()
        for name, sec_group in self.security_groups.items():
            returns_df[name] = sec_group.returns()

        return returns_df.sum(axis=1)

