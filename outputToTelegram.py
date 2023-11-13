import datetime

import utils


def print_anomal_volume(arr_times_direction, ticker, marketdata,
                                                                     volume,
                                                                     times, lastPrice, todayOpenPrice,
                                                                     old_arr_times_direction, old_time_for_direction,
                                                                     storage_volume=0):


    tmp_buy=0
    tmp_sell=0

    Price_Now=utils.cast_money(lastPrice.last_prices[0].price)
    Price_candel_Open=utils.cast_money(marketdata.candle.open)
    Price_candel_Open_today=utils.cast_money(todayOpenPrice.candles[0].open)

    percentage_change = utils.compare_numbers(Price_Now, Price_candel_Open)
    percentage_change_today = utils.compare_numbers(Price_Now,  Price_candel_Open_today)


    # Сравнение минутного времени
    if marketdata.candle.time.minute == old_time_for_direction:
        for i, el in enumerate(old_arr_times_direction):
            if el[0] == marketdata.candle.figi:
                tmp_buy = el[1]
                tmp_sell = el[2]
                # Обновляем значение в списке, нужно заново пересчитывать % для следующего обьема
                old_arr_times_direction[i][1] = 0
                # Обновляем значение в списке, нужно заново пересчитывать % для следующего обьема
                old_arr_times_direction[i][2] = 0
                # print(tmp_buy, "tmp_buy")
                # print(tmp_sell, "tmp_sell")
        print("Минутное время старое")
    else:
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
    buy_percentage = round(tmp_buy / total_volume * 100)
    sell_percentage = round(tmp_sell / total_volume * 100)

    if buy_percentage > sell_percentage:
        # Подчеркивание текста "покупка"
        buy_text = "\u0332".join("покупка")
        sell_text = "продажа"
    elif sell_percentage > buy_percentage:
        # Подчеркивание текста "продажа"
        buy_text = "покупка"
        sell_text = "\u0332".join("продажа")
    else:
        # Если цифры равны, не подчеркиваем ничего
        buy_text = "покупка"
        sell_text = "продажа"
    # print("marketdata",marketdata.candle)
    if total_volume != 0:
        # print(storage_volume,"storage_volume")
        # print(marketdata.candle, "marketdata.candle.volume")
        print(ticker, "пороговый обьем: ", volume,  "Обьем: ", float(round(float((marketdata.candle.volume-storage_volume)/100)))/10,"M₽",  '\n',
              "число раз за минуту: ", times + 1,'\n',
              "текущая цена: ",  Price_Now,'\n',
              "Изменение цены:",'\n'
            "  на объеме:", percentage_change, "%",'\n',
              "  за день:",  percentage_change_today, "%",'\n',
              f"{buy_text}: {buy_percentage}%, {sell_text}: {sell_percentage}%",
              "Время: ",datetime.datetime.now().replace(microsecond=0))
    else:
        print(ticker, "пороговый обьем: ", volume, "Обьем: ",
              float(round(float((marketdata.candle.volume - storage_volume) / 100))) / 10, "M₽", '\n',
              "число раз за минуту: ", times + 1, '\n',
              "Не удалось определить пропорцию покупки/продажи:", '\n',
              "Время: ", datetime.datetime.now().replace(microsecond=0))

