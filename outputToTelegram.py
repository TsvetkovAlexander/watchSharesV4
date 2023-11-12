import datetime

import utils


def print_anomal_volume(arr_times_direction,ticker, marketdata, volume, times, lastPrice, storage_volume):
    tmp_buy=0
    tmp_sell=0

    Price_Now=utils.cast_money(lastPrice.last_prices[0].price)
    Price_candel_Open=utils.cast_money(marketdata.candle.open)


    percentage_change = utils.compare_numbers(Price_Now, Price_candel_Open)


    # print(arr_times_direction, "arr_times_direction")
    for i, el in enumerate(arr_times_direction):
        if el[0] == marketdata.candle.figi:

            tmp_buy = el[1]
            tmp_sell = el[2]
            # Обновляем значение в списке, нужно заново пересчитывать % для следующего обьема
            arr_times_direction[i][1] = 0
            # Обновляем значение в списке, нужно заново пересчитывать % для следующего обьема
            arr_times_direction[i][2] = 0
            # print(tmp_buy, "tmp_buy")
            # print(tmp_sell, "tmp_sell")
    total_volume = tmp_buy+tmp_sell
    if total_volume != 0:
        # print(storage_volume,"storage_volume")
        print(marketdata.candle, "marketdata.candle.volume")
        print(ticker, "пороговый обьем: ", volume,  "Обьем: ", float(round(float((marketdata.candle.volume-storage_volume)/100)))/10,"M₽",  '\n',
              "число раз за минуту: ", times + 1,'\n',
              "текущая цена: ",  Price_Now,'\n',
              print(f"Изменение цены:"),
            print(f"    на объеме:", percentage_change, "%"),
                 "покупка:", round(tmp_buy / total_volume * 100), "%", "продажа:", round(tmp_sell / total_volume * 100), "%",'\n',
              "Время: ",datetime.datetime.now().replace(microsecond=0))
    else:
        print(ticker, "пороговый обьем: ", volume, "Обьем: ",
              float(round(float((marketdata.candle.volume - storage_volume) / 100))) / 10, "M₽", '\n',
              "число раз за минуту: ", times + 1, '\n',
              "Не удалось определить пропорцию покупки/продажи:", '\n',
              "Время: ", datetime.datetime.now().replace(microsecond=0))

