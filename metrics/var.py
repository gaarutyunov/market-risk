import numpy as np
import pandas as pd

import typing
import arch
import pmdarima as pmdarima


def calculate_historical(returns: pd.DataFrame, alpha: float = 0.99, horizon: int = 10) -> float:
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
    horizon: int = 1
) -> float:
    """GARCH VaR

    :param horizon: Горизонт предсказания
    :param returns: Датафрейм с доходностью инструмента
    :param alpha: Параметр альфа для VaR
    :param dist: Распределение
    :return:
    """
    mdl = arch.arch_model(returns * 100, dist=dist)
    res = mdl.fit(disp="off")
    forecast = res.forecast(reindex=False, horizon=horizon)
    q = res.std_resid.quantile(1 - alpha)
    mu = forecast.mean.values.ravel()[-1].item()
    sigma = np.sqrt(forecast.variance.values.ravel()[-1].item())
    var = -(mu + sigma * q) / 100

    return var


def calculate_arima_garch(
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
    horizon: int = 1
) -> float:
    """ARIMA-GARCH VaR

    :param horizon: Горизонт предсказания
    :param returns: Датафрейм с доходностью инструмента
    :param alpha: Параметр альфа для VaR
    :param dist: Распределение
    :return:
    """
    # fit ARIMA on returns
    arima_model = pmdarima.auto_arima(returns * 100)
    arima_residuals = arima_model.arima_res_.resid

    # fit a GARCH(1,1) model on the residuals of the ARIMA model
    mdl = arch.arch_model(arima_residuals, dist=dist)

    res = mdl.fit(disp="off")
    # Use GARCH to predict the residual
    forecast = res.forecast(reindex=False, horizon=horizon)
    q = np.quantile(res.std_resid, 1 - alpha)

    # Use ARIMA to predict mu
    mu = arima_model.predict(n_periods=horizon)[0]
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


