# В этом файле скрипты, не относящиеся к main.
# Служебные скрипты, для разового запуска.


import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from tinkoff.invest import Client, InstrumentStatus
from tinkoff.invest.services import InstrumentsService, MarketDataService

load_dotenv()

TOKEN = os.environ['TOKEN']
db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_host = os.environ['DB_HOST']
print(db_name)
print(db_user)
print(db_password)
print(db_host)

conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)

excel_data_df = pd.read_excel('dataExl.xlsx')


def update_available_ticker():
    with Client(TOKEN) as cl:
        instruments = cl.instruments

        r = instruments.shares(instrument_status=InstrumentStatus.INSTRUMENT_STATUS_ALL).instruments
        ru_share = []
        for i in range(len(r)):
            rub = r[i].currency == 'rub'
            available_flag = r[i].buy_available_flag
            trade_available_flag = r[i].api_trade_available_flag

            if all([rub, available_flag, trade_available_flag]):
                d = dict(figi=r[i].figi,
                         ticker=r[i].ticker,
                         name=r[i].name,
                         lot=r[i].lot,
                         short_enabled_flag=r[i].short_enabled_flag,
                         units=r[i].min_price_increment.units,
                         nano=r[i].min_price_increment.nano)
                ru_share.append(d)
        print(f'Готово. Всего записей: {len(ru_share)}')

        df = pd.DataFrame(ru_share)
        df.to_excel('dataExl.xlsx', index=False)


def update_tables():
    for index, row in excel_data_df[['figi', 'ticker']].iterrows():
        try:
            with conn.cursor() as curs:
                curs.execute(f"""DELETE FROM {row['ticker']}""")
                curs.execute(f"""DROP TABLE IF EXISTS {row['ticker']}""")
                curs.execute(f"""CREATE TABLE IF NOT EXISTS {row['ticker']} (
                                   date_time TIMESTAMP with time zone null,
                                   volume integer,
                                   PRIMARY KEY (date_time));""")
                conn.commit()
        except Exception as error:
            print(row[0])
            print(error)


def make_mapping():
    with conn.cursor() as curs:
        curs.execute(f"""CREATE TABLE IF NOT EXISTS ticker_mapping (
                           ticker varchar(255),
                           figi varchar(255),
                           name varchar(255),
                           PRIMARY KEY (ticker));""")
        conn.commit()

    for index, row in excel_data_df[['figi', 'ticker', 'name']].iterrows():
        query = sql.SQL(
            """insert into ticker_mapping values ({ticker}, {figi}, {name}) 
            on conflict (ticker) do update SET 
                ticker = EXCLUDED.ticker, 
                figi = EXCLUDED.figi, 
                name = EXCLUDED.name""").format(
            ticker=sql.Literal(row['ticker']),
            figi=sql.Literal(row['figi']),
            name=sql.Literal(row['name']))
        print(query.as_string(conn))
        try:
            with conn.cursor() as curs:
                curs.execute(query)
                conn.commit()
        except Exception as error:
            print(row[0])
            print(error)


def add_column():
    with conn.cursor() as curs:
        curs.execute(f"""ALTER TABLE ticker_mapping ADD name varchar(255);""")
        conn.commit()
