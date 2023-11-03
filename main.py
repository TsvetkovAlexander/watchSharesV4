import time
import pandas as pd
from tinkoff.invest import Client, RequestError, CandleInterval, HistoricCandle
import pytz
import asyncio
import xlsxwriter
from tinkoff.invest import AsyncClient, CandleInterval
from tinkoff.invest.utils import now
from datetime import datetime, time
import psycopg2

import utils, monitoringVolume, getNewHistoryData

with open('token.txt') as f:
    TOKEN = f.read()  # ТОКЕН тинькоф апи


async def main():
    spisokMaxVolume = await getNewHistoryData.getHistoryCandels()  # Загружаем в базу новые данные за последние дни и получаем значения аномальных обьемов

    asyncio.run(await monitoringVolume.monitoring(spisokMaxVolume))  # Запускаем функцию мониторинга аномальных обьемов


if __name__ == "__main__":
    asyncio.run(main())
