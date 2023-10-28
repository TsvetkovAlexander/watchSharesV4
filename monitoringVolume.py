import datetime

import pandas as pd
from tinkoff.invest import Client, RequestError, CandleInterval, HistoricCandle
import pytz
import asyncio
import os
from main import main
from tinkoff.invest.utils import now
from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    InfoInstrument,
    SubscriptionInterval,
)
from tinkoff.invest.async_services import AsyncMarketDataStreamManager
from tinkoff.invest.services import MarketDataStreamManager
import utils
with open('token.txt') as f:
    TOKEN = f.read() # ТОКЕН тинькоф апи

from tinkoff.invest import (
    CandleInstrument,
    Client,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
    Candle,
    GetCandlesRequest,
    SubscribeTradesRequest
)


TOKEN ="t.zTgMZTzAlZBsY8lJveJAdmngmvMGCsG7Z2h8FjEcSBGJSuRx1IKxgIt85vYmkHZDHdyfwQtO0e_FX1VKK3sHvw"

from tinkoff.invest import (
    CandleInstrument,
    Client,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
    Candle,
GetCandlesRequest
)


async def monitoring(spisokMaxVolume):
    async def request_iterator():
        yield MarketDataRequest(  # Стрим соединение на получение Аномальных обьемов по свечам
                    subscribe_candles_request=SubscribeCandlesRequest(
                        subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                        instruments=utils.arrInstrument, # сюда закидываем все элементы, по которым работает стрим

                    ),
                )
        yield MarketDataRequest(
            subscribe_trades_request=SubscribeTradesRequest(  # Стрим соединение на получение всех сделок
                subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
                instruments=[ #  пока написал 1 элемент сбербанка для простоты
                    CandleInstrument(
                        figi="BBG004730N88",
                    )
                ],
            )
        )
        while True:
            await asyncio.sleep(1)



    arrTimesDirecion = []  # Массив всех сделок по текущей минуте формата :ФИГИ, обьемы на покупку, обьемы на продажу
    currentTimeForDirection =datetime.datetime.now().hour
    arrTimesVolume = [] # 1 элемент время, остальные фиги сколько раз было повторений в минуту. Чем больше повторений фиги тем больше раз повторений  аномальных обьемов было в минуту
    async with AsyncClient(TOKEN) as client:
        async for marketdata in client.market_data_stream.market_data_stream(
                request_iterator()
        ):


            # if marketdata.trade: # Ниже пытаюсь сделать код, который считает сделки на покупку и продажу и закидывает их в arrTimesDirecion, не доделал
            #     print(marketdata.trade) # если получаем свечу
            #     now = datetime.datetime.now().minute # берем текущее минутное время, нужно для работы с обновлением по минутам
            #     print(arrTimesDirecion, currentTimeForDirection, "")
            #     if currentTimeForDirection != now:    #Если изменилась минута, обновляем массив и закидываем первую сделку.
            #         arrTimesDirecion = []
            #         currentTimeForDirection =now
            #         if str(marketdata.trade.direction) == "TradeDirection.TRADE_DIRECTION_BUY": # сделка на покупку
            #             print("STAAAAAAAAAAAAAAAAAAAAT BUY")
            #             el = marketdata.trade.figi, marketdata.trade.quantity, 0 # третье значение на продажу= 0
            #             arrTimesDirecion.append(el)
            #
            #         if str(marketdata.trade.direction) == "TradeDirection.TRADE_DIRECTION_SELL": # сделка на продажу
            #             el = marketdata.trade.figi,0 ,  marketdata.trade.quantity # второе значение на покупку = 0
            #             arrTimesDirecion.append(el)
            #             print("STAAAAAAAAAAAAAAAAAAAAT SELL")
            #
            #
            #     else: # Если у нас уже была хотя бы 1 сделка на новой минуте, то просто закидываем сюда новые, нужно реализовать поиск по массиву и суммирование покупок и продаж по каждой акции
            #         if str(marketdata.trade.direction) == "TradeDirection.TRADE_DIRECTION_BUY":
            #             # tmpArrSell = tmpArrSell + marketdata.trade.quantity
            #             print(marketdata.trade.quantity, "BHhsfdalsjkhfdskjahfanlkjhfsalkjsbfafa")
            #         if str(marketdata.trade.direction) == "TradeDirection.TRADE_DIRECTION_SELL":
            #             # tmpArrBuy = tmpArrBuy + marketdata.trade.quantity
            #             print(marketdata.trade.quantity, "BHhsfdalsjkhfdskjahfanlkjhfsalkjsbfafa")


            if marketdata.candle: #  Второе стрим соедение по обьемам для каждой акции, если получаем обьем, то.

                            # print(marketdata.candle)
                            # print(spisokMaxVolume)
                            # if start_time <= now.time() <= end_time:
                            #
                            # if marketdata.candle.figi=="BBG004730N88" and marketdata.candle.volume > 1:
                            #     print(marketdata.candle)

                if marketdata.candle.volume > 1: #  Если обьем больше 1
                    for element in spisokMaxVolume:  # получаем значение для каждого элемента,который мы получили из базы
                        ticker, volume, figi_spisok = element
                        if figi_spisok == marketdata.candle.figi: #  если нашли совпадение по фиги из стрима и из массива, полученного из базы
                            if marketdata.candle.volume > volume: # если срабатывает аномальный обьем
                                now = datetime.datetime.now().minute #  получаем текущее время для обновления массивов аномальных обьемов
                                if arrTimesVolume and arrTimesVolume[0] != now: #  если новая минута, то все обновляем
                                    arrTimesVolume = []
                                    arrTimesVolume.append(now)
                                    arrTimesVolume.append(figi_spisok) #
                                    print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЬЕМ")
                                else:

                                    times = arrTimesVolume.count(figi_spisok) #  считаем сколько раз было уже аномальных обьемов
                                    if times == 0:
                                        print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЬЕМ")
                                        arrTimesVolume.append(figi_spisok) # добавляем в список фиги
                                        print(arrTimesVolume)
                                    if times == 1 and marketdata.candle.volume - volume > volume: # если 2 повторения, то аномальный обьем должен быть в 2 раза больше, поэтому - volume
                                        print(ticker, marketdata.candle.volume, volume,
                                              "АНОМАЛЬНЫЙ ОБЬЕМ дважды за минуту")
                                        arrTimesVolume.append(figi_spisok)
                                        print(arrTimesVolume)
                                    if times == 2 and marketdata.candle.volume - volume * 2 > volume:
                                        print(ticker, marketdata.candle.volume, volume,
                                              "АНОМАЛЬНЫЙ ОБЬЕМ трижды за минуту")
                                        arrTimesVolume.append(figi_spisok)
                                    if times == 3 and marketdata.candle.volume - volume * 3 > volume:
                                        print(ticker, marketdata.candle.volume, volume,
                                              "АНОМАЛЬНЫЙ ОБЬЕМ 4 за минуту")
                                        arrTimesVolume.append(figi_spisok)







### НИЖЕ ненужный тестовый мусор, можно удалять, я оставил для себя


# def monitoring(spisokMaxVolume):
#     def request_iterator():
#         yield MarketDataRequest(
#             subscribe_candles_request=SubscribeCandlesRequest(
#                 subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
#                 instruments=utils.arrInstrument,
#
#             )
#         )
#         while True:
#             time.sleep(1)
#
#     # now = datetime.now().time()
#     # if start_time <= now:
#     #     if end_time >= now:
#     #         print('LJCKD',now)
#     # return 0
#
#
#     # print("ВРЕМЯ ВЫШЛО ")
#     # return 0
#     # arrTimesVolume = []
#
#     with Client(TOKEN) as client:
#         for marketdata in client.market_data_stream.market_data_stream(
#             request_iterator()
#         ):
#             if marketdata.candle:
#                 # print(marketdata.candle)
#                 # print(spisokMaxVolume)
#                 # if start_time <= now.time() <= end_time:
#
#                 # if marketdata.candle.figi=="BBG004730N88" and marketdata.candle.volume > 1:
#                 #     print(marketdata.candle)
#
#                 if marketdata.candle.volume > 1:
#                     for element in spisokMaxVolume:
#                         ticker, volume, figi_spisok = element
#                         if figi_spisok == marketdata.candle.figi:
#                             if marketdata.candle.volume > volume:
#                                 now=datetime.datetime.now().minute
#                                 if arrTimesVolume and arrTimesVolume[0] != now:
#                                     arrTimesVolume=[]
#                                     arrTimesVolume.append(now)
#                                     arrTimesVolume.append(figi_spisok)
#                                     print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЬЕМ")
#                                 else:
#
#                                     times=arrTimesVolume.count(figi_spisok)
#                                     if times == 0:
#                                         print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЬЕМ")
#                                         arrTimesVolume.append(figi_spisok)
#                                         print(arrTimesVolume)
#                                     if times == 1 and marketdata.candle.volume - volume > volume:
#                                         print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЬЕМ дважды за минуту")
#                                         arrTimesVolume.append(figi_spisok)
#                                         print(arrTimesVolume)
#                                     if times == 2 and marketdata.candle.volume - volume * 2 > volume:
#                                         print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЬЕМ трижды за минуту")
#                                         arrTimesVolume.append(figi_spisok)
#                                     if times == 3 and marketdata.candle.volume - volume * 3 > volume:
#                                         print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЬЕМ 4 за минуту")
#                                         arrTimesVolume.append(figi_spisok)


                                    #     arrTimesVolume.append(el)
                                # el=figi_spisok
                                # arrTimesVolume.append(now)

                                # print(arrTimesVolume,"arrTimesVolumearrTimesVolumearrTimesVolumearrTimesVolumearrTimesVolumearrTimesVolumearrTimesVolumearrTimesVolumearrTimesVolumearrTimesVolumearrTimesVolumearrTimesVolume")
                                #
                                # if marketdata.candle.volume - volume > volume:
                                #     print(marketdata.candle.volume - volume , volume, "АНОМАЛЬНЫЙ ОБЬЕМ")


# if __name__ == "monitoringVolume":
#     while True:
#         now = datetime.datetime.now()
#         start_time = datetime.time(10, 0)
#         end_time = datetime.time(16, 40)
#         nightStart=datetime.time(21, 39,59)
#         nightEnd = datetime.time(21, 45, 00)
#         start_time1 = datetime.time(16, 41)
#         end_time1 = datetime.time(23, 50)




        # if nightStart <= now.time() <= nightEnd and     tmp == 1:
        #     async def run():
        #         spisokMaxVolume = await main()  # Используйте await для получения значения
        #         print(spisokMaxVolume)
        #
        #
        #     asyncio.run(run())
        #
        #     tmp=0
        # if start_time <= now.time() <= end_time or start_time1 <= now.time() <= end_time1 :
        #     monitoring(spisokMaxVolume)
        # else:
        #     time_to_wait = (datetime.datetime.combine(datetime.date.today(), start_time) - now).total_seconds()
        #     if time_to_wait > 0:
        #         print("Функция main() будет запущена в 12:00. Ожидание...")
        #         time.sleep(time_to_wait)
        #     else:
        #         print("Функция main() будет запущена в текущий момент времени. Ожидание...")
        #         time.sleep(1)







# if __name__ == "monitoringVolume":
#     while True:
#         now = datetime.datetime.now()
#         start_time = datetime.time(10, 0)
#         end_time = datetime.time(16, 40)
#         nightStart=datetime.time(21, 39,59)
#         nightEnd = datetime.time(21, 45, 00)
#         start_time1 = datetime.time(16, 41)
#         end_time1 = datetime.time(23, 50)
#
#
#
#
#         if nightStart <= now.time() <= nightEnd and     tmp == 1:
#             async def run():
#                 spisokMaxVolume = await main()  # Используйте await для получения значения
#                 print(spisokMaxVolume)
#
#
#             asyncio.run(run())
#
#             tmp=0
#         if start_time <= now.time() <= end_time or start_time1 <= now.time() <= end_time1 :
#             monitoring(spisokMaxVolume)
#         else:
#             time_to_wait = (datetime.datetime.combine(datetime.date.today(), start_time) - now).total_seconds()
#             if time_to_wait > 0:
#                 print("Функция main() будет запущена в 12:00. Ожидание...")
#                 time.sleep(time_to_wait)
#             else:
#                 print("Функция main() будет запущена в текущий момент времени. Ожидание...")
#                 time.sleep(1)
#

# subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE,
#                instruments=[
#                    CandleInstrument(
#                        figi="BBG004730N88",
#                    ),

# CandleInstrument(
#     figi="BBG006L8G4H1",
#     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
# ),
# CandleInstrument(
#     figi="BBG004S682Z6",
#     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
# ),
# CandleInstrument(
#     figi="TCS00A103X66",
#     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
# ),
# CandleInstrument(
#     figi="BBG004S68598",
#     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
# ),
# CandleInstrument(
#     figi="BBG000R04X57",
#     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
# ),
# CandleInstrument(
#     figi="BBG004S68B31",
#     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
# )
