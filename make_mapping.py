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


def make_mapping():
    with conn.cursor() as curs:
        curs.execute(f"""CREATE TABLE IF NOT EXISTS ticker_mapping (
                           ticker varchar(255),
                           figi varchar(255),
                           name varchar(255),
                           lot integer,
                           short_enabled_flag boolean,
                           units integer,
                           nano integer,
                           PRIMARY KEY (ticker));""")
        conn.commit()

    for index, row in excel_data_df[
        ['figi', 'ticker', 'name', 'lot', 'short_enabled_flag', 'units', 'nano']].iterrows():
        query = sql.SQL(
            """insert into ticker_mapping values ({ticker}, {figi}, {name}, {lot}, {short_enabled_flag}, {units}, {nano}) 
            on conflict (ticker) do update SET 
                ticker = EXCLUDED.ticker, 
                figi = EXCLUDED.figi, 
                name = EXCLUDED.name,
                lot = EXCLUDED.lot, 
                short_enabled_flag = EXCLUDED.short_enabled_flag, 
                units = EXCLUDED.units,
                nano = EXCLUDED.nano""").format(
            ticker=sql.Literal(row['ticker']),
            figi=sql.Literal(row['figi']),
            name=sql.Literal(row['name']),
            lot=sql.Literal(row['lot']),
            short_enabled_flag=sql.Literal(row['short_enabled_flag']),
            units=sql.Literal(row['units']),
            nano=sql.Literal(row['nano']))

        try:
            with conn.cursor() as curs:
                curs.execute(query)
                conn.commit()
        except Exception as error:
            print(row[0])
            print(error)


if __name__ == '__main__':
    make_mapping()
