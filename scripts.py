# В этом файле скрипты, не относящиеся к main.
# Служебные скрипты, для разового запуска.


import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

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


def add_columns_to_ticker():
    for index, row in excel_data_df[['figi', 'ticker']].iterrows():
        try:
            with conn.cursor() as curs:
                query = sql.SQL(
                    """ALTER TABLE {ticker} ADD COLUMN IF NOT EXISTS close_price float;
                        ALTER TABLE {ticker} ADD COLUMN IF NOT EXISTS volume_rub float;""").format(
                    ticker=sql.Identifier(row['ticker']))

                curs.execute(query)
                conn.commit()
        except Exception as error:
            print(row[0])
            print(error)


def add_column():
    with conn.cursor() as curs:
        curs.execute(f"""ALTER TABLE ticker_mapping ADD name varchar(255);""")
        conn.commit()
