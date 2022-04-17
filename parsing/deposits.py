from pathlib import Path

import pandas as pd


__DEPOSITS_PATH__ = Path("..", "data", "deposits")


def get_deposit_rates(currency: str = 'RUB') -> pd.DataFrame:
    """Возвращает информацию по ставкам депозитов с 2014 по 2022 гг по заданной валюте.

    Источник: https://www.cbr.ru/vfs/statistics/pdko/int_rat/deposits.xlsx

    Методика расчета: https://www.cbr.ru/Content/Document/File/132282/regulatory_rates_met.pdf

    Значение заголовков:

    * demand: "до востребова-ния"**
    * lt_30d_with_demand: до 30 дней, включая "до востребова-ния"
    * lt_30d_no_demand: до 30 дней, кроме "до востребова-ния"
    * 31d_to_90d: от 31 до 90 дней
    * 91d_to_180d: от 91 до 180 дней
    * 181d_to_1y: от 181 дня до 1 года
    * lt_1y_with_demand: до 1 года, включая "до востребова-ния"
    * lt_1y_no_demand: до 1 года, кроме "до востребова-ния"
    * 1y_to_3y: от 1 года до 3 лет
    * gt_3y: свыше 3 лет
    * gt_1y: свыше 1 года

    :return: :class:`pandas.DataFrame` со ставками депозитов
    """
    return pd.read_pickle(Path(str(__DEPOSITS_PATH__), currency + '.pickle'))
