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
from settings import GlobalSetting

load_dotenv()
# Загрузка переменных окружения
TOKEN = os.environ['TOKEN']

DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']

connection = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)


async def load_db(df, days_before=GlobalSetting.days_before, log=False):
    # Функция загрузки данных в БД
    # Параметр days_before указывается на количество дней на сколько нужно загрузить статистику
    if log:
        print("Заполнение БД запущено".center(80, '-'), datetime.now())

    for index, row in tqdm(df.iterrows(), total=len(df)):
        table_exist = check_ticker_table_exist(ticker=row['ticker'])
        if not table_exist:
            if log:
                print(f"Не найдена таблица {row['ticker']}".center(80, '-'))
            create_ticker_table(ticker=row['ticker'])

        await load_ticker_data(ticker=row['ticker'], figi=row['figi'], days_before=days_before)

    if log:
        print("Заполнение БД завершено".center(80, '-'), datetime.now())


async def load_ticker_data(ticker, figi, days_before=GlobalSetting.days_before):
    # Функция добавляет информацию по одному тикеру
    candles = await get_candles(figi=figi, days_before=days_before)
    insert_candles(ticker=ticker, figi=figi, candles=candles)


async def delete_old_ticker(ticker, conn=connection, how_old=GlobalSetting.how_old):
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


async def update_db(df, delete_old_data=True, log=False):
    # Функция обновляет данные в БД до последней актуальной записи
    if log:
        print("Обновление БД запущено".center(80, '-'), datetime.now())

    for index, row in tqdm(df.iterrows(), total=len(df)):
        table_exist = check_ticker_table_exist(ticker=row['ticker'])
        if not table_exist:
            if log:
                print(f"Не найдена таблица {row['ticker']}".center(80, '-'))
            create_ticker_table(ticker=row['ticker'])
        if delete_old_data:
            await delete_old_ticker(ticker=row['ticker'])
        await update_ticker_data(ticker=row['ticker'], figi=row['figi'])

    if log:
        print("Обновление БД завершено".center(80, '-'), datetime.now())


async def update_ticker_data(ticker, figi):
    # Функция обновляет данные в БД до последней актуальной записи для одного тикера
    last_date = get_last_date(ticker=ticker)

    if last_date is None:
        await load_ticker_data(ticker=ticker, figi=figi, days_before=1)
        return None

    candles = await get_candles(figi=figi, last_date=last_date)
    insert_candles(ticker=ticker, figi=figi, candles=candles)


async def get_candles(figi, days_before=None, last_date=None):
    if days_before:
        current_date = now().replace(hour=0, minute=0, second=0, microsecond=0)
        from_moment = current_date - timedelta(days=days_before)
    else:
        from_moment = last_date

    candles = []

    async with AsyncClient(TOKEN) as client:
        async for candle in client.get_all_candles(
                figi=figi,
                from_=from_moment,
                interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        ):
            candles.append(candle)

    return candles


def insert_candles(ticker, figi, candles, conn=connection):
    tz = timezone('Europe/Moscow')

    for candle in candles:
        time = candle.time.astimezone(tz)
        volume = candle.volume
        close_price = utils.cast_money(candle.close)
        volume_rub = volume * close_price

        data = {'figi': figi,
                'ticker': ticker,
                'time': time,
                'volume': volume,
                'close_price': close_price,
                'volume_rub': volume_rub}

        if not utils.is_holiday(data['time']):
            time = data['time'].strftime("%Y-%m-%d %H:%M:%S")
            with conn.cursor() as curs:
                query = sql.SQL("""insert into {ticker} 
                                    values ({time}, {volume}, {close_price}, {volume_rub}) 
                                    on  conflict (date_time) do update SET 
                                    date_time = EXCLUDED.date_time,
                                    volume = {volume},
                                    close_price = {close_price},
                                    volume_rub = {volume_rub}
                                    """).format(
                    ticker=sql.Identifier(data['ticker']),
                    time=sql.Literal(time),
                    volume=sql.Literal(data['volume']),
                    close_price=sql.Literal(data['close_price']),
                    volume_rub=sql.Literal(data['volume_rub'])
                )
                try:
                    curs.execute(query)
                    conn.commit()

                except Exception as error:
                    print(error)


def check_ticker_table_exist(ticker, conn=connection):
    try:
        with conn.cursor() as curs:
            query = sql.SQL("""SELECT EXISTS (
                            SELECT FROM 
                                pg_tables
                            WHERE 
                                schemaname = 'public' AND 
                                tablename  = {ticker}
                            )""").format(
                ticker=sql.Literal(ticker)
            )
            curs.execute(query)
            return curs.fetchone()[0]
    except Exception as error:
        print(error)


def create_ticker_table(ticker, conn=connection):
    try:
        with conn.cursor() as curs:
            query = sql.SQL("""CREATE TABLE IF NOT EXISTS {ticker} (
                               date_time TIMESTAMP with time zone null,
                               volume integer, close_price float, volume_rub float,
                               PRIMARY KEY (date_time));""").format(
                ticker=sql.Identifier(ticker))
            curs.execute(query)
            conn.commit()
    except Exception as error:
        print(error)


def get_last_date(ticker, conn=connection):
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


def get_ticker_mapping(ticker=None, figi=None, conn=connection):
    assert figi is None or ticker is None, 'Надо задать либо ticker либо figi'

    if ticker:
        with conn.cursor() as curs:
            query = sql.SQL("select * from ticker_mapping where ticker={ticker}").format(
                ticker=sql.Literal(ticker),
            )
            try:
                curs.execute(query)
                mapping = curs.fetchone()
            except Exception as error:
                print(error)

    if figi:
        with conn.cursor() as curs:
            query = sql.SQL("select * from ticker_mapping where figi={figi}").format(
                figi=sql.Literal(figi),
            )
            try:
                curs.execute(query)
                mapping = curs.fetchone()
            except Exception as error:
                print(error)

    mapping = {'ticker': mapping[0],
               'figi': mapping[1],
               'name': mapping[2],
               'lot': mapping[3],
               'short_enabled_flag': mapping[4],
               'units': mapping[5],
               'nano': mapping[6]}

    return mapping


def get_ticker_data(ticker, conn=connection):
    try:
        with conn.cursor() as curs:
            query = sql.SQL("SELECT volume, close_price, volume_rub FROM {ticker}").format(
                ticker=sql.Identifier(ticker)
            )
            curs.execute(query)
            rows = curs.fetchall()
            return rows
    except Exception as error:
        print(error)
