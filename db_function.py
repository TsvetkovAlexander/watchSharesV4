import os
from datetime import timedelta, timezone, datetime

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from pytz import timezone
from tinkoff.invest import AsyncClient, CandleInterval
from tinkoff.invest.utils import now
from tqdm import tqdm

import utils

load_dotenv()
# Загрузка переменных окружения
TOKEN = os.environ['TOKEN']

DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']

connection = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)


async def load_db(df, conn=connection, days_before=30, log=False):
    # Функция загрузки данных в БД
    # Параметр days_before указывается на количество дней на сколько нужно загрузить статистику
    if log:
        print("Заполнение БД запущено".center(80, '-'), datetime.now())

    for index, row in tqdm(df.iterrows(), total=len(df)):
        await load_ticker_data(row['ticker'], row['figi'], conn, days_before)

    if log:
        print("Заполнение БД завершено".center(80, '-'), datetime.now())


async def load_ticker_data(ticker, figi, conn, days_before=30):
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
                    query = sql.SQL("insert into {ticker} \
                                        values ({time}, {volume}) \
                                        on conflict (date_time) do update \
                                        SET date_time = EXCLUDED.date_time").format(
                        ticker=sql.Identifier(ticker),
                        time=sql.Literal(time),
                        volume=sql.Literal(volume)
                    )
                    try:
                        curs.execute(query)
                        conn.commit()

                    except Exception as error:
                        print(error)


async def delete_old_ticker(ticker, conn, how_old=30):
    current_date = datetime.now()
    border_date = current_date - timedelta(days=how_old)
    border_date = border_date.date().strftime("%Y-%m-%d")

    with conn.cursor() as curs:
        query = sql.SQL("""delete from {ticker} where date_time < {border_date}""").format(
            ticker=sql.Identifier(ticker),
            border_date=sql.Literal(border_date)
        )
        try:
            curs.execute(query)
            conn.commit()

        except Exception as error:
            print(error)


def check_ticker_table_exist(ticker, conn):
    try:
        with conn.cursor() as curs:
            query = sql.SQL("""SELECT EXISTS (
                            SELECT FROM 
                                pg_tables
                            WHERE 
                                schemaname = 'public' AND 
                                tablename  = '{ticker}'
                            )""").format(
                ticker=sql.Identifier(ticker)
            )
            curs.execute(query)
            return curs.fetchone()[0]
    except Exception as error:
        print(error)


def create_ticker_table(ticker, conn):
    try:
        with conn.cursor() as curs:
            query = sql.SQL("""CREATE TABLE IF NOT EXISTS {ticker} (
                               date_time TIMESTAMP with time zone null,
                               volume integer,
                               PRIMARY KEY (date_time));""").format(
                ticker=sql.Identifier(ticker))
            curs.execute(query)
            conn.commit()
    except Exception as error:
        print(error)


async def update_db(df, conn=connection, delete_old_data=True, log=False):
    # Функция обновляет данные в БД до последней актуальной записи
    if log:
        print("Обновление БД запущено".center(80, '-'), datetime.now())

    for index, row in tqdm(df.iterrows(), total=len(df)):
        table_exist = check_ticker_table_exist(row['ticker'], conn)
        if not table_exist:
            if log:
                print(f"Не найдена таблица {row['ticker']}".center(80, '-'))
            create_ticker_table(row['ticker'], conn)
        if delete_old_data:
            await delete_old_ticker(row['ticker'], conn)
        await update_ticker(row['ticker'], row['figi'], conn)

    if log:
        print("Обновление БД завершено".center(80, '-'), datetime.now())


def get_last_date(ticker, conn):
    try:
        with conn.cursor() as curs:
            query = sql.SQL("select max(date_time) from {ticker}").format(
                ticker=sql.Identifier(ticker),
            )
            curs.execute(query)
            last_date = curs.fetchone()[0]
    except Exception as error:
        print(error)
    return last_date


async def update_ticker(ticker, figi, conn):
    # Функция обновляет данные в БД до последней актуальной записи для одного тикера
    async with AsyncClient(TOKEN) as client:
        last_date = get_last_date(ticker, conn)

        if last_date is None:
            await load_ticker_data(ticker, figi, conn, days_before=1)
            return None

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
                    query = sql.SQL("insert into {ticker} \
                                        values ({time}, {volume}) \
                                        on  conflict (date_time) do update SET \
                                        date_time = EXCLUDED.date_time").format(
                        ticker=sql.Identifier(ticker),
                        time=sql.Literal(time),
                        volume=sql.Literal(volume)
                    )
                    try:
                        curs.execute(query)
                        conn.commit()

                    except Exception as error:
                        print(error)


def get_ticker_volume(ticker, conn=connection):
    try:
        with conn.cursor() as curs:
            query = sql.SQL("SELECT volume FROM {ticker}").format(
                ticker=sql.Identifier(ticker)
            )
            curs.execute(query)
            rows = curs.fetchall()
            return rows
    except Exception as error:
        print(error)
