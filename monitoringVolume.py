import asyncio
import datetime
import os
import warnings
from datetime import timedelta, timezone
from dotenv import load_dotenv
from tinkoff.invest import (
    AsyncClient,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscribeTradesRequest
)
from tinkoff.invest import AsyncClient, CandleInterval
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
    old_arr_times_direction = []
    pricesCandel = []
    current_time_for_direction = datetime.datetime.now().hour + 100
    old_time_for_direction = datetime.datetime.now().hour + 100
    current_time_for_volume = datetime.datetime.now().hour + 100
    arr_times_figi_volume = []
    total_sum = 0
    # lastPrice = None
    # todayOpenPrice= None
    storage_volume = 0

    # 1 элемент время, остальные фиги сколько раз было повторений в минуту. Чем больше
    # повторений фиги тем больше раз повторений аномальных объемов было в минуту
    async with AsyncClient(TOKEN) as client:
        async for marketdata in client.market_data_stream.market_data_stream(
                request_iterator()
        ):

            # async def find_prices(figi_current, marketdata, arr_times_figi_volume, start_time, end_time):
            #     elFigiVolume = [figi_current, marketdata.candle.volume]
            #     arr_times_figi_volume.append(elFigiVolume)
            #     lastPrice = await client.market_data.get_last_prices(figi=[figi_current])
            #     todayOpenPrice = await client.market_data.get_candles(
            #         figi=figi_current,
            #         from_=start_time, to=end_time,
            #         interval=CandleInterval.CANDLE_INTERVAL_1_MIN
            #     )
            #     return lastPrice, todayOpenPrice

            if marketdata.trade:
                # print(marketdata.trade)  # если получаем свечу
                # берем текущее минутное время, нужно для работы с обновлением по минутам
                now = datetime.datetime.now().minute
                # print(arrTimesDirection, current_time_for_direction, " Весь наш массив сделок")
                # Заходим в if если первый запуск либо наступила новая минута
                if current_time_for_direction != now:
                    old_arr_times_direction = arr_times_direction
                    arr_times_direction = []
                    old_time_for_direction = current_time_for_direction
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
                # print(marketdata)  # если получаем свечу
                # if marketdata.candle.volume > 1:
                # получаем значение для каждого элемента, который мы получили из базы
                for ticker, value in dict_max_volume.items():
                    ticker, volume, figi_current, name = ticker, value['volume'], value['figi'], value['name']
                    # если нашли совпадение по фиги из стрима и из массива, полученного из базы
                    if figi_current == marketdata.candle.figi:
                        # если срабатывает аномальный объем
                        if marketdata.candle.volume * ((utils.cast_money(marketdata.candle.high)+utils.cast_money(marketdata.candle.low))/2) > volume:
                            medium_price = (utils.cast_money(marketdata.candle.high) + utils.cast_money(
                                marketdata.candle.low)) / 2
                            # если 2 повторения, то аномальный объем должен быть в 2 раза больше, поэтому - volume

                            # получаем текущее время для обновления массивов аномальных объемов
                            now = datetime.datetime.now().minute
                            # если новая минута, то все обновляем
                            if current_time_for_volume != now:
                                # Это массив наших фиги, где мы считаем их повторения. Приравниваем его к 0
                                # 1 элемент время, далее фиги
                                arr_times_figi_volume = []
                                current_time_for_volume = now
                                await outputToTelegram.print_anomal_volume(client, ticker, marketdata,
                                                                           volume,
                                                                           figi_current,
                                                                           arr_times_direction,
                                                                           arr_times_figi_volume,
                                                                           old_arr_times_direction,
                                                                           old_time_for_direction,medium_price,name,
                                                                           times=0, storage_volume=0,storage_volumeRub=0 )

                            else:
                                # считаем сколько раз было уже аномальных объемов
                                times = sum(1 for item in arr_times_figi_volume if item[0] == figi_current)

                                if times == 0:
                                    await outputToTelegram.print_anomal_volume(client, ticker, marketdata,
                                                                               volume,
                                                                               figi_current,
                                                                               arr_times_direction,
                                                                               arr_times_figi_volume,
                                                                               old_arr_times_direction,
                                                                               old_time_for_direction,medium_price,
                                                                               times, storage_volume=0,storage_volumeRub=0)

                                storage_volume,storage_volumeRub = utils.countVolume(arr_times_figi_volume, figi_current)
                                if times > 0 and (marketdata.candle.volume * medium_price) > (volume + storage_volumeRub):
                                    print("marketdata.candle.volume",marketdata.candle.volume,"medium_price",medium_price, " marketdata.candle.volume * medium_price",marketdata.candle.volume * medium_price, " volume",volume, "storage_volumeRub", storage_volumeRub, "volume + storage_volumeRub",volume + storage_volumeRub)
                                    times = sum(1 for item in arr_times_figi_volume if item[0] == figi_current)
                                    await outputToTelegram.print_anomal_volume(client, ticker, marketdata,
                                                                               volume,
                                                                               figi_current,
                                                                               arr_times_direction,
                                                                               arr_times_figi_volume,
                                                                               old_arr_times_direction,
                                                                               old_time_for_direction,medium_price,name,
                                                                               times, storage_volume, storage_volumeRub)

