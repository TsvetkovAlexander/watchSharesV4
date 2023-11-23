import os
from datetime import datetime

import numpy as np
import pandas as pd
from dotenv import load_dotenv

from db_function import load_db, update_db, get_ticker_data

load_dotenv()
# Загрузка переменных окружения
TOKEN = os.environ['TOKEN']

excel_data_df = pd.read_excel('dataExl.xlsx')


def get_max_volume(ticker, quantile=50, log=False):
    # Расчет аномального объема для тикера.
    # Параметр quantile - процентиль (по умолчанию задан 90, в вызове функции можно изменить)
    try:
        rows = get_ticker_data(ticker)
        volume = np.array([row[0] for row in rows])
        close_price = np.array([row[1] for row in rows])
        volume_rub = np.array([row[2] for row in rows])

        # Рабочая величина, с чем надо работать. По желанию заменить
        value = volume

        if len(value) < 500:
            rounded_percentile = None
        else:
            percentile = np.percentile(value, quantile)
            rounded_percentile = round(percentile)

        if log == 'Full':
            print(f'{ticker} {quantile}-ый процентиль - {rounded_percentile}')

    except Exception as error:
        print(error)
        rounded_percentile = None

    return ticker, rounded_percentile


def get_all_max_volume(df, log=False):
    if log:
        print("Запуск получения аномальных объемов".center(80, '-'), datetime.now())

    dict_max_volume = dict()
    for index, row in df.iterrows():
        ticker, volume = get_max_volume(row['ticker'])
        lot = row['lot']
        figi = row['figi']
        name = row['name']

        if volume is not None:
            dict_max_volume[ticker] = {'figi': figi, 'volume': volume, 'name': name, 'lot': lot}

    if log:
        print("Получение аномальных объемов завершено".center(80, '-'), datetime.now())
    return dict_max_volume


async def get_history_candles():
    # Из таблицы удаляются тикеры по которым нет данных
    test_df = excel_data_df[~excel_data_df.ticker.isin([])][['ticker', 'figi', 'name', 'lot']]


    # await update_db(test_df[test_df.ticker == 'SBER'], conn, log=True)
    # dict_max_volume = get_max_volume(test_df[test_df.ticker == 'SBER'], conn, log=True)

    await update_db(test_df)
    dict_max_volume = get_all_max_volume(test_df)

    return dict_max_volume
