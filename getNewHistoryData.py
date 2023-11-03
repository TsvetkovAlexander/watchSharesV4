import time
import pandas as pd
from tinkoff.invest import Client, RequestError, CandleInterval, HistoricCandle
import pytz
import asyncio
import xlsxwriter
from tinkoff.invest import AsyncClient, CandleInterval
from tinkoff.invest.utils import now

from datetime import datetime, date, time, timezone, timedelta
import psycopg2
from datetime import date, datetime
import utils, monitoringVolume

TOKEN = ""


async def getHistoryCandels():
    db_name = 'postgres'
    db_user = 'postgres'
    db_password = 'root'
    db_host = 'localhost'

    conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)
    async with AsyncClient(TOKEN) as client:

        excel_data_df = pd.read_excel('dataExl.xlsx')  # смотрим файл эксель со списком акций

        # Получение списка значений из второго столбца
        column_values = excel_data_df['figi'].tolist()  # список фиги
        list_names = excel_data_df['ticker'].tolist()  # список имен
        current_date1 = now().replace(hour=0, minute=0, second=0, microsecond=0)  # делаем дату 00:00
        # for i in range(len(column_values)):  # НУЖНО РАСКОМЕНТИТЬ КОД НИЖЕ - получение данных и закидка их в базу
        #     async for candle in client.get_all_candles(
        #             figi=column_values[i],
        #             from_=current_date1 - timedelta(days=1),  # Устанавливаем насколько дней назад мы получаем данные
        #             interval=CandleInterval.CANDLE_INTERVAL_1_MIN,
        #     ):
        #         candle.time.replace(tzinfo=timezone.utc)
        #         tz = datetime.strptime('+0300', '%z').tzinfo
        #         dt_in_03_tz = str(candle.time.astimezone(tz))
        #         dt_in_03_tz = dt_in_03_tz.partition('+')[0]
        #         d = dict(volume=candle.volume, time=dt_in_03_tz, figi=column_values[i], ticker=list_names[i])
        #         # print(d)
        #
        #         volume = d['volume']
        #         time = d['time']
        #         figi = d['figi']
        #         ticker = d['ticker']
        #         holiday = utils.get_weekend_dates()
        #         if time[:10] not in holiday:
        #             with conn.cursor() as curs:
        #                 try:
        #
        #                     curs.execute(
        #                         """insert into {} values ({}, '{}', '{}', '{}')""".format(ticker, volume, time, figi,
        #                                                                                   ticker))
        #                     conn.commit()
        #
        #                 except (Exception, psycopg2.DatabaseError) as error:
        #                     print(error)

    with conn.cursor() as curs:
        try:
            spisokMaxVolume = []  # пустой список аномальных обьемов
            for table_name in list_names:  # идем по каждой акции их списка
                # Ниже код до conn.commit() для для удаления всех повторяющихся строк в каждой таблице по times
                curs.execute("SELECT DISTINCT ON (times) * FROM {}".format(table_name))
                rows = curs.fetchall()

                # Создание временной таблицы для хранения уникальных строк
                temp_table_name = "temp_" + table_name
                create_temp_table_query = "CREATE TEMP TABLE {} (LIKE {}) ON COMMIT DROP".format(temp_table_name,
                                                                                                 table_name)
                curs.execute(create_temp_table_query)

                # Вставка уникальных строк во временную таблицу
                for row in rows:
                    insert_query = "INSERT INTO {} (volume, times, figi, ticker) VALUES (%s, %s, %s, %s)".format(
                        temp_table_name)
                    curs.execute(insert_query, (row[0], row[1], row[2], row[3]))

                # Удаление дубликатов и обновление исходной таблицы
                delete_query = "DELETE FROM {}".format(table_name)
                curs.execute(delete_query)
                insert_query = "INSERT INTO {} SELECT * FROM {}".format(table_name, temp_table_name)
                curs.execute(insert_query)

                # Фиксируем изменения
                conn.commit()

                # Получаем все обьемы  по первой строке row[0] и сортируем их
                values = [row[0] for row in rows]
                values.sort()

                # Находим индекс, соответствующий 99-му процентилю
                index = int(len(values) * 0.9)

                # Устанавливаем значение как максимальное из чисел, превосходящих 99% других чисел, но не превышающих 1% самых больших чисел
                value = max(values[:index + 1])

                # Округляем число до ближайшего целого
                rounded_value = round(value)
                print(table_name)
                print("Число, превосходящее 99% других чисел, но не превышающее 1% самых больших чисел:", rounded_value)
                _, _, figi, _ = rows[2]  # Замените 2 на соответствующий индекс строки
                # Получение первого значения из результата запроса

                NameAndVolumeCurrently = table_name, rounded_value, figi

                spisokMaxVolume.append(NameAndVolumeCurrently)
                # asyncio.run(monitoringVolume.monitoring(spisokMaxVolume))
            print(spisokMaxVolume)

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    # Закрытие соединения с базой данных
    conn.close()
    return spisokMaxVolume
