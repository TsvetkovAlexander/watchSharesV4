import asyncio
import datetime
import os
import warnings

from dotenv import load_dotenv
from tinkoff.invest import (
    AsyncClient,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscribeTradesRequest
)

import utils, outputToTelegram
# Предупреждение никуда не пропадает, просто мы его игнорируем, что бы оно не засоряло вывод
warnings.filterwarnings('ignore')
load_dotenv()

TOKEN = os.environ['TOKEN']


async def monitoring(dict_max_volume):
    async def request_iterator():
        yield MarketDataRequest(  # Стрим соединение на получение Аномальных объемов по свечам
            subscribe_candles_request=SubscribeCandlesRequest(
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                instruments=utils.arrInstrument,  # сюда закидываем все элементы, по которым работает стрим
            ),
        )
        yield MarketDataRequest(
            subscribe_trades_request=SubscribeTradesRequest(  # Стрим соединение на получение всех сделок
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                instruments=utils.arrTradeInstrument
            )
        )
        while True:
            await asyncio.sleep(1)

    arr_times_direction = []  # Массив всех сделок по текущей минуте формата: ФИГИ, объемы на покупку, объемы на продажу
    current_time_for_direction = datetime.datetime.now().hour + 100
    current_time_for_volume = datetime.datetime.now().hour + 100
    arr_times_volume = []
    # 1 элемент время, остальные фиги сколько раз было повторений в минуту. Чем больше
    # повторений фиги тем больше раз повторений аномальных объемов было в минуту
    async with AsyncClient(TOKEN) as client:
        async for marketdata in client.market_data_stream.market_data_stream(
                request_iterator()
        ):
            if marketdata.trade:
                # print(marketdata.trade)  # если получаем свечу
                # берем текущее минутное время, нужно для работы с обновлением по минутам
                now = datetime.datetime.now().minute
                # print(arrTimesDirection, current_time_for_direction, " Весь наш массив сделок")
                # Заходим в if если первый запуск либо наступила новая минута
                if current_time_for_direction != now:
                    arr_times_direction = []
                    current_time_for_direction = now
                    if str(marketdata.trade.direction.name) == "TRADE_DIRECTION_BUY":
                        # у элемента 3 значение (продажа) = 0
                        el = [marketdata.trade.figi, marketdata.trade.quantity, 0]
                        arr_times_direction.append(el)
                    elif str(marketdata.trade.direction.name) == "TRADE_DIRECTION_SELL":
                        # у элемента 2 значение (покупка) = 0,
                        el = [marketdata.trade.figi, 0, marketdata.trade.quantity]
                        arr_times_direction.append(el)
                else:
                    if str(marketdata.trade.direction.name) == "TRADE_DIRECTION_BUY":
                        figi_exists = False
                        for i, el in enumerate(arr_times_direction):
                            # у уже есть элемент в массиве
                            if el[0] == marketdata.trade.figi:
                                figi_exists = True
                                # print(el[0], "el[0] ")
                                # пересчитываем его значения на покупку
                                arr_times_direction[i] = [el[0], el[1] + marketdata.trade.quantity, el[2]]
                                # print(updated_el, "EL BUY")
                                break
                        if not figi_exists:
                            # добавляем новый, если его нет в списке
                            el = [marketdata.trade.figi, marketdata.trade.quantity, 0]
                            arr_times_direction.append(el)
                    elif str(marketdata.trade.direction.name) == "TRADE_DIRECTION_SELL":
                        figi_exists = False
                        for i, el in enumerate(arr_times_direction):
                            # у уже есть элемент в массиве
                            if el[0] == marketdata.trade.figi:
                                figi_exists = True
                                # print(el[0], "el[0] ")
                                # пересчитываем его значения на продажу
                                arr_times_direction[i] = [el[0], el[1], el[2] + marketdata.trade.quantity]
                                # print(updated_el, "EL SELL")
                                break
                        # добавляем новый, если его нет в списке
                        if not figi_exists:
                            el = [marketdata.trade.figi, 0, marketdata.trade.quantity]
                            arr_times_direction.append(el)

            # Второе стрим соединение по объемам для каждой акции, если получаем объем, то печатаем его
            if marketdata.candle:
                # Если объем больше 1
                # if marketdata.candle.volume > 1:
                    # получаем значение для каждого элемента, который мы получили из базы
                for ticker, value in dict_max_volume.items():
                    ticker, volume, figi_current = ticker, value['volume'], value['figi']
                    # если нашли совпадение по фиги из стрима и из массива, полученного из базы
                    if figi_current == marketdata.candle.figi:
                        # если срабатывает аномальный объем
                        if marketdata.candle.volume > volume:
                            # print(arr_times_volume)
                            # получаем текущее время для обновления массивов аномальных объемов
                            now = datetime.datetime.now().minute
                            # если новая минута, то все обновляем
                            if current_time_for_volume != now:
                                # Это массив наших фиги, где мы считаем их повторения. Приравниваем его к 0
                                # 1 элемент время, далее фиги
                                arr_times_volume=[]
                                current_time_for_volume = now
                                times = arr_times_volume.count(figi_current)
                                arr_times_volume.append(figi_current)
                                outputToTelegram.print_anomal_volume(arr_times_direction, ticker, marketdata, volume,
                                                          times)
                            else:
                                # считаем сколько раз было уже аномальных объемов
                                times = arr_times_volume.count(figi_current)
                                if times == 0:

                                    outputToTelegram.print_anomal_volume(arr_times_direction, ticker, marketdata, volume,
                                                              times)

                                    arr_times_volume.append(figi_current)  # добавляем в список фиги
                                # если 2 повторения, то аномальный объем должен быть в 2 раза больше, поэтому - volume
                                if times > 0 and marketdata.candle.volume > volume*(times + 1):
                                    # print(arr_times_direction, "arr_times_direction1")
                                    outputToTelegram.print_anomal_volume(arr_times_direction, ticker, marketdata, volume,
                                                              times)
                                    arr_times_volume.append(figi_current)

