# В этом файле скрипты, не относящиеся к main.
# Служебные скрипты, для разового запуска.


import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_name = os.environ['DB_NAME']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_host = os.environ['DB_HOST']

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


def make_mapping():
    with conn.cursor() as curs:
        curs.execute(f"""CREATE TABLE IF NOT EXISTS ticker_mapping (
                           ticker varchar(255),
                           figi varchar(255),
                           PRIMARY KEY (ticker));""")
        conn.commit()

    for index, row in excel_data_df[['figi', 'ticker']].iterrows():
        try:
            with conn.cursor() as curs:
                curs.execute(f"insert into ticker_mapping \
                                values ('{row['ticker']}', '{row['figi']}') \
                                on  conflict (ticker) do update SET ticker = EXCLUDED.ticker")
                conn.commit()
        except Exception as error:
            print(row[0])
            print(error)
