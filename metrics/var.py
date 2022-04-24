import numpy as np
import pandas as pd

import typing
import arch
import statsmodels.api as sm


def calculate_historical(returns: pd.DataFrame, alpha: float = 0.99) -> float:
    """Исторический VaR

    :param returns: Датафрейм с доходностью инструмента
    :param alpha: Параметр альфа для VaR
    :return:
    """
    return -np.percentile(returns.values, (1 - alpha) * 100, method="inverted_cdf")


def calculate_garch(
    returns: pd.DataFrame,
    alpha: float = 0.99,
    dist: typing.Literal[
        "normal",
        "gaussian",
        "t",
        "studentst",
        "skewstudent",
        "skewt",
        "ged",
        "generalized error",
    ] = "normal",
) -> float:
    """GARCH VaR

    :param returns: Датафрейм с доходностью инструмента
    :param alpha: Параметр альфа для VaR
    :param dist: Распределение
    :return:
    """
    mdl = arch.arch_model(returns * 100, dist=dist)
    res = mdl.fit(disp="off")
    forecast = res.forecast(reindex=False)
    q = res.std_resid.quantile(1 - alpha)
    mu = forecast.mean.values.item()
    sigma = np.sqrt(forecast.variance.values.item())
    var = -(mu + sigma * q) / 100
    return var


def calculate_sarimax(
    returns: pd.DataFrame,
    model_params: dict,
    alpha: float = 0.99,
    ) -> float:
    """SARIMAX VaR

    :param returns: Датафрейм с доходностью инструмента
    :param model_params: Словарь с параметрами SARIMAX
    :param alpha: Параметр альфа для VaR
    :param dist: Распределение
    :return:
    """
    mdl = sm.tsa.statespace.SARIMAX(returns * 100, **model_params)
    mdl = mdl.fit()
    forecast = mdl.predict(reindex=False)
    q = mdl.resid.quantile(1 - alpha)
    mu = forecast.mean.values.item()
    sigma = np.sqrt(forecast.variance.values.item())
    var = -(mu + sigma * q) / 100
    return var


def calculate(
    returns: pd.Series,
    calc_func: typing.Callable[[pd.DataFrame, float], float],
    window_length: int = 252,
    *args,
    **kwargs
):
    return returns.rolling(window=window_length, closed="left").apply(
        calc_func,
        args=args,
        kwargs=kwargs,
    )
