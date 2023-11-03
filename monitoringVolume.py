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

# with open('token.txt') as f:
#     TOKEN = f.read()  # ТОКЕН тинькоф апи
TOKEN = ""
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

    arrTimesDirecion = []  # Массив всех сделок по текущей минуте формата :ФИГИ, обьемы на покупку, обьемы на продажу
    currentTimeForDirection = datetime.datetime.now().hour
    arrTimesVolume = []  # 1 элемент время, остальные фиги сколько раз было повторений в минуту. Чем больше повторений фиги тем больше раз повторений  аномальных обьемов было в минуту
    async with AsyncClient(TOKEN) as client:
        async for marketdata in client.market_data_stream.market_data_stream(
                request_iterator()
        ):
            if marketdata.trade:
                # print(marketdata.trade)  # если получаем свечу
                now = datetime.datetime.now().minute  # берем текущее минутное время, нужно для работы с обновлением по минутам
                # print(arrTimesDirecion, currentTimeForDirection, " Весь наш массив сделок")
                if currentTimeForDirection != now:
                    arrTimesDirecion = []
                    currentTimeForDirection = now
                    if str(marketdata.trade.direction) == "TradeDirection.TRADE_DIRECTION_BUY":

                        el = [marketdata.trade.figi, marketdata.trade.quantity, 0] # у элемента 3 значение (продажа) = 0,
                        arrTimesDirecion.append(el)
                    elif str(marketdata.trade.direction) == "TradeDirection.TRADE_DIRECTION_SELL":
                        el = [marketdata.trade.figi, 0, marketdata.trade.quantity] # у элемента 2 значение (покупка) = 0,
                        arrTimesDirecion.append(el)
                else:
                    if str(marketdata.trade.direction) == "TradeDirection.TRADE_DIRECTION_BUY":
                        figi_exists = False
                        for i, el in enumerate(arrTimesDirecion):
                            if el[0] == marketdata.trade.figi: # у уже есть элемент в массиве
                                figi_exists = True
                                # print(el[0], "el[0] ")
                                updated_el = [el[0], el[1] + marketdata.trade.quantity, el[2]]  # пересчитываем его значения на покупку
                                arrTimesDirecion[i] = updated_el
                                # print(updated_el, "EL BUY")
                                break
                        if not figi_exists:
                            el = [marketdata.trade.figi, marketdata.trade.quantity, 0] # добавляем новый, если его нет в списке
                            arrTimesDirecion.append(el)
                    elif str(marketdata.trade.direction) == "TradeDirection.TRADE_DIRECTION_SELL":
                        figi_exists = False
                        for i, el in enumerate(arrTimesDirecion):
                            if el[0] == marketdata.trade.figi: # у уже есть элемент в массиве
                                figi_exists = True
                                # print(el[0], "el[0] ")
                                updated_el = [el[0], el[1], el[2] + marketdata.trade.quantity]  # пересчитываем его значения на продажу
                                arrTimesDirecion[i] = updated_el
                                # print(updated_el, "EL SELL")
                                break
                        if not figi_exists: # добавляем новый, если его нет в списке
                            el = [marketdata.trade.figi,0, marketdata.trade.quantity]
                            arrTimesDirecion.append(el)

            if marketdata.candle:  # Второе стрим соедение по обьемам для каждой акции, если получаем обьем, то печатаем его
                tmpBuy=0.0
                tmpSell=0.0
                if marketdata.candle.volume > 1:  # Если обьем больше 1
                    for element in spisokMaxVolume:  # получаем значение для каждого элемента,который мы получили из базы
                        ticker, volume, figi_current = element
                        if figi_current == marketdata.candle.figi:  # если нашли совпадение по фиги из стрима и из массива, полученного из базы
                            if marketdata.candle.volume > volume:  # если срабатывает аномальный обьем
                                now = datetime.datetime.now().minute  # получаем текущее время для обновления массивов аномальных обьемов
                                if arrTimesVolume and arrTimesVolume[0] != now:  # если новая минута, то все обновляем
                                    arrTimesVolume = [] # это массив наших фиги, где мы считаем их повторяния. Приравниваем его к 0
                                    arrTimesVolume.append(now) # 1 элемент время, далее фиги
                                    arrTimesVolume.append(figi_current)  # 1 добавляем первый фиги


                                    totalVolume = 0
                                    for i, el in enumerate(arrTimesDirecion):
                                        if el[0] == marketdata.candle.figi:
                                            tmpBuy = el[1]
                                            tmpSell = el[2]
                                            arrTimesDirecion[i][1] = 0  # Обновляем значение в списке, нужно заново пересчитывать % для следующего обьема
                                            arrTimesDirecion[i][2] = 0  # Обновляем значение в списке, нужно заново пересчитывать % для следующего обьема
                                            totalVolume = tmpBuy + tmpSell
                                            # print(tmpBuy, "tmpBuy")
                                            # print(tmpSell, "tmpSell")

                                    if totalVolume != 0:
                                        print(marketdata.candle)
                                        print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЪЕМ",
                                              "покупка:", tmpBuy / totalVolume * 100, "%", "продажа:",
                                              tmpSell / totalVolume * 100, "%")
                                    else:
                                        print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЪЕМ",
                                              "покупка: 0%", "продажа: 0%")
                                else:

                                    times = arrTimesVolume.count(figi_current)  # считаем сколько раз было уже аномальных обьемов
                                    if times == 0:
                                        totalVolume=0
                                        for i, el in enumerate(arrTimesDirecion):
                                            if el[0] == marketdata.candle.figi:
                                                tmpBuy = el[1]
                                                tmpSell = el[2]
                                                arrTimesDirecion[i][1] = 0  # Обновляем значение в списке, нужно заново пересчитывать % для следующего обьема
                                                arrTimesDirecion[i][2] = 0  # Обновляем значение в списке
                                                totalVolume = tmpBuy + tmpSell
                                                # print(tmpBuy, "tmpBuy")
                                                # print(tmpSell, "tmpSell")

                                        if totalVolume != 0:
                                            print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЪЕМ",
                                                  "покупка:", tmpBuy / totalVolume * 100, "%", "продажа:",
                                                  tmpSell / totalVolume * 100, "%")
                                        else:
                                            print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЪЕМ",
                                                  "покупка: 0%", "продажа: 0%")
                                        # print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЬЕМ")
                                        arrTimesVolume.append(figi_current)  # добавляем в список фиги
                                        # print(arrTimesVolume)
                                    if times == 1 and marketdata.candle.volume - volume > volume:  # если 2 повторения, то аномальный обьем должен быть в 2 раза больше, поэтому - volume
                                        totalVolume = 0
                                        for i, el in enumerate(arrTimesDirecion):
                                            if el[0] == marketdata.candle.figi:
                                                tmpBuy = el[1]
                                                tmpSell = el[2]
                                                arrTimesDirecion[i][1] = 0  # Обновляем значение в списке, нужно заново пересчитывать % для следующего обьема
                                                arrTimesDirecion[i][2] = 0  # Обновляем значение в списке
                                                totalVolume = tmpBuy + tmpSell
                                                # print(tmpBuy, "tmpBuy")
                                                # print(tmpSell, "tmpSell")

                                        if totalVolume != 0:
                                            print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЪЕМ дважды",
                                                  "покупка:", tmpBuy / totalVolume * 100, "%", "продажа:",
                                                  tmpSell / totalVolume * 100, "%")
                                        else:
                                            print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЪЕМ дважды",
                                                  "покупка: 0%", "продажа: 0%")
                                        arrTimesVolume.append(figi_current)
                                        # print(arrTimesVolume)
                                    if times == 2 and marketdata.candle.volume - volume * 2 > volume:
                                        totalVolume = 0
                                        for i, el in enumerate(arrTimesDirecion):
                                            if el[0] == marketdata.candle.figi:
                                                tmpBuy = el[1]
                                                tmpSell = el[2]
                                                arrTimesDirecion[i][1] = 0  #Обновляем значение в списке, нужно заново пересчитывать % для следующего обьема
                                                arrTimesDirecion[i][2] = 0  # Обновляем значение в списке
                                                totalVolume = tmpBuy + tmpSell
                                                # print(tmpBuy, "tmpBuy")
                                                # print(tmpSell, "tmpSell")

                                        if totalVolume != 0:
                                            print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЪЕМ трижды",
                                                  "покупка:", tmpBuy / totalVolume * 100, "%", "продажа:",
                                                  tmpSell / totalVolume * 100, "%")
                                        else:
                                            print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЪЕМ трижды",
                                                  "покупка: 0%", "продажа: 0%")
                                        arrTimesVolume.append(figi_current)
                                    if times == 3 and marketdata.candle.volume - volume * 3 > volume:
                                        totalVolume = 0
                                        for i, el in enumerate(arrTimesDirecion):
                                            if el[0] == marketdata.candle.figi:
                                                tmpBuy = el[1]
                                                tmpSell = el[2]
                                                arrTimesDirecion[i][1] = 0  # Обновляем значение в списке
                                                arrTimesDirecion[i][2] = 0  # Обновляем значение в списке
                                                totalVolume = tmpBuy + tmpSell
                                                # print(tmpBuy, "tmpBuy")
                                                # print(tmpSell, "tmpSell")

                                        if totalVolume != 0:
                                            print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЪЕМ четыре раза",
                                                  "покупка:", tmpBuy / totalVolume * 100, "%", "продажа:",
                                                  tmpSell / totalVolume * 100, "%")
                                        else:
                                            print(ticker, marketdata.candle.volume, volume, "АНОМАЛЬНЫЙ ОБЪЕМ четыре раза",
                                                  "покупка: 0%", "продажа: 0%")
                                        arrTimesVolume.append(figi_current)
