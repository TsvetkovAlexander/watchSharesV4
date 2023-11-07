import os
from datetime import timedelta, timezone, datetime

import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from pytz import timezone
from tinkoff.invest import AsyncClient, CandleInterval
from tinkoff.invest.utils import now
from tqdm import tqdm

import utils

load_dotenv()
# Загрузка переменных окружения
TOKEN = os.environ['TOKEN']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_host = os.environ['DB_HOST']

connection = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)
excel_data_df = pd.read_excel('dataExl.xlsx')


async def load_db(df, days_before=1, log=False):
    # Функция загрузки данных в БД
    # Параметр days_before указывается на количество дней на сколько нужно загрузить статистику
    if log:
        print("Заполнение БД запущено".center(80, '-'), datetime.now())

    for index, row in tqdm(df.iterrows(), total=len(df)):
        await load_ticker(row['ticker'], row['figi'], days_before)

    if log:
        print("Заполнение БД завершено".center(80, '-'), datetime.now())


async def load_ticker(ticker, figi, conn, days_before=1):
    # Функция добавляет информацию по одному тикеру
    current_date = now().replace(hour=0, minute=0, second=0, microsecond=0)

    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
                figi=figi,
                from_=current_date - timedelta(days=days_before),
                interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):

            tz = timezone('Europe/Moscow')

            volume = candle.volume
            time = candle.time.astimezone(tz)

            if not utils.is_holiday(time):
                time = time.strftime("%Y-%m-%d %H:%M:%S")
                with conn.cursor() as curs:
                    try:
                        curs.execute(f"insert into {ticker} \
                                        values ('{time}', {volume}) \
                                        on  conflict (date_time) do update SET date_time = EXCLUDED.date_time")
                        conn.commit()

                    except Exception as error:
                        print(error)


async def update_db(df, log=False):
    # Функция обновляет данные в БД до последней актуальной записи
    if log:
        print("Обновление БД запущено".center(80, '-'), datetime.now())

    for index, row in tqdm(df.iterrows(), total=len(df)):
        await update_ticker(row['ticker'], row['figi'], connection)

    if log:
        print("Обновление БД завершено".center(80, '-'), datetime.now())


async def update_ticker(ticker, figi, conn):
    # Функция обновляет данные в БД до последней актуальной записи для одного тикера
    async with AsyncClient(TOKEN) as client:
        try:
            with conn.cursor() as curs:
                curs.execute(f"select max(date_time) from {ticker}")
                last_date = curs.fetchone()[0]
        except Exception as error:
            print(error)

        async for candle in client.get_all_candles(
                figi=figi,
                from_=last_date,
                interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):

            tz = timezone('Europe/Moscow')

            volume = candle.volume
            time = candle.time.astimezone(tz)

            if not utils.is_holiday(time):
                time = time.strftime("%Y-%m-%d %H:%M:%S")
                with conn.cursor() as curs:
                    try:
                        curs.execute(f"insert into {ticker} \
                                        values ('{time}', {volume}) \
                                        on  conflict (date_time) do update SET date_time = EXCLUDED.date_time")
                        conn.commit()

                    except Exception as error:
                        print(error)


def get_all_max_volume(df, log=False):
    if log:
        print("Запуск получения аномальных объемов".center(80, '-'), datetime.now())

    dict_max_volume = dict()
    for index, row in df.iterrows():
        ticker, figi, volume = get_max_volume(row['figi'], row['ticker'], connection)
        dict_max_volume[ticker] = {'figi': figi, 'volume': volume}

    if log:
        print("Получение аномальных объемов завершено".center(80, '-'), datetime.now())
    return dict_max_volume


def get_max_volume(figi, ticker, conn, quantile=90, log=False):
    # Расчет аномального объема для тикера.
    # Параметр quantile - процентиль (по умолчанию задан 90, в вызове функции можно изменить)
    try:
        with conn.cursor() as curs:
            curs.execute(f"SELECT volume FROM {ticker}")
            rows = curs.fetchall()

        values = np.array([row[0] for row in rows])
        percentile = np.percentile(values, quantile)
        rounded_percentile = round(percentile)

        if log == 'Full':
            print(f'{ticker} {quantile}-ый процентиль - {rounded_percentile}')

    except Exception as error:
        print(error)
        rounded_percentile = None

    return ticker, figi, rounded_percentile


async def get_history_candles():
    # Из таблицы удаляются тикеры по которым нет данных
    test_df = excel_data_df[~excel_data_df.ticker.isin(['VKCO', 'ISKJ', 'SFTL'])][['ticker', 'figi']]

    # await update_db(test_df[test_df.ticker == 'SBER'], conn, log=True)
    # dict_max_volume = get_max_volume(test_df[test_df.ticker == 'SBER'], conn, log=True)

    await update_db(test_df)
    dict_max_volume = get_all_max_volume(test_df)

    return dict_max_volume
