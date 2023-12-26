import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from tinkoff.invest import Client, InstrumentStatus

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


if __name__ == '__main__':
    update_available_ticker()
