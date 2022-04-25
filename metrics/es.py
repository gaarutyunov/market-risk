import typing

import pandas as pd


def calculate(
    returns: pd.Series,
    calc_func: typing.Callable[[pd.DataFrame, float], float],
    window_length: int = 252,
    *args,
    **kwargs
):
    def func(returns, *args, **kwargs):
        VaR = calc_func(returns, *args, **kwargs)

        return returns[returns < (-VaR)].mean()

    return returns.rolling(window=window_length, closed="left").apply(
        func,
        args=args,
        kwargs=kwargs,
    )
