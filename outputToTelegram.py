import datetime
import os
import utils
import telebot

# Указываем токен вашего бота
API_TOKEN = os.environ['API_TOKEN']

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Функция для вывода данных в канал Telegram
def Output_telegram():
    channel_id = -1002101810065  # Айди вашего канала
    message = "Ваши данные для вывода в канал"
    bot.send_message(channel_id, message)

async def print_anomal_volume(client, ticker, marketdata,
                              volume,
                              figi_current,
                              arr_times_direction,
                              arr_times_figi_volume,
                              old_arr_times_direction, old_time_for_direction,medium_price,name,
                              times, storage_volume,storage_volumeRub):

    current_time = datetime.datetime.now().time()
    tmp_buy = 0
    tmp_sell = 0
    # print("storage_volume",storage_volume)
    lastPrice, todayOpenPrice = await utils.find_prices(figi_current, marketdata,
                                                        arr_times_figi_volume,medium_price,
                                                        client)


    Price_Now = utils.cast_money(lastPrice.last_prices[0].price)
    Price_candel_Open = utils.cast_money(marketdata.candle.open)
    # print(marketdata.candle,"marketdata.candle")
    # print(todayOpenPrice,ticker,"todayOpenPrice")

    Price_candel_Open_today = utils.cast_money(todayOpenPrice.candles[0].open)
    if current_time.hour == 10 and current_time.minute == 0:
        Price_candel_Open_today = Price_candel_Open
    # print(Price_candel_Open_today, "Price_candel_Open_today")
    percentage_change = utils.compare_numbers(Price_Now, Price_candel_Open)
    percentage_change_today = utils.compare_numbers(Price_Now, Price_candel_Open_today)

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
    total_volume = tmp_buy + tmp_sell
    if total_volume > 0:
        buy_percentage = round(tmp_buy / total_volume * 100)
        sell_percentage = round(tmp_sell / total_volume * 100)
    else:
        buy_percentage = 0
        sell_percentage = 0

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
    channel_id = -1002101810065
    if total_volume != 0:
        # print(marketdata.candle.volume, "marketdata.candle.volume")
        # print(storage_volume, "storage_volume")
        # print(marketdata.candle.volume - storage_volume, "marketdata.candle.volume - storage_volume")
        # print(storage_volume,"storage_volume")
        # print(marketdata.candle, "marketdata.candle.volume")
        # print(storage_volume, "storage_volume:", volume, "Обьем:",storage_volumeRub, "storage_volumeRub", marketdata.candle.volume, "marketdata.candle.volume")

         # Айди вашего канала
        def arrow(percentage):
            return "⬆️" if float(percentage) > 0 else "⬇️"

        # Используйте эту функцию для определения значения для вывода
        arrow_symbol = arrow(percentage_change)

        # Составьте сообщение с желаемым форматированием
        message = (arrow_symbol + " " + "#" + ticker + " " + str(
                    round(float((marketdata.candle.volume * medium_price - storage_volumeRub) / 1000000), 2)) + "M₽" +
                   str(percentage_change) + "%" + '\n' +
                   "🔷 Аномальный объем" + '\n' +
                   name + '\n' +
                   "Объём: " + str(
                    round(float((marketdata.candle.volume * medium_price - storage_volumeRub) / 1000000), 2)) + "M₽ (" +
                   str(marketdata.candle.volume - storage_volume) + " лотов)" + '\n' +
                   "Покупка: " + str(buy_percentage) + "% Продажа: " + str(sell_percentage) + "%" + '\n' +
                   "Цена: " + str(Price_Now) + "₽" + '\n' +
                   "Изменение цены:" + '\n' +
                   "    на объеме: " + str(percentage_change) + "%" + '\n' +
                   "    за сегодня: " + str(percentage_change_today) + "%" + '\n' +
                   "Время: " + str(datetime.datetime.now().replace(microsecond=0)))

        bot.send_message(channel_id, message)

        print(message)
        # print(ticker, " ", name,'\n',
        #       "пороговый обьем:", volume, "Обьем:",
        #       float(round(float((marketdata.candle.volume * medium_price  - storage_volumeRub) / 100))) / 10, "M₽",
        #       "(", (marketdata.candle.volume - storage_volume), "лотов)", '\n',
        #       "число раз за минуту:", times + 1, '\n',
        #       "текущая цена:", Price_Now, '\n',
        #       "Изменение цены:", '\n'
        #                          "  на объеме:", percentage_change, "%", '\n',
        #       "  за день:", percentage_change_today, "%", '\n',
        #       f"{buy_text}: {buy_percentage}%, {sell_text}: {sell_percentage}%",
        #       "Время:", datetime.datetime.now().replace(microsecond=0))

    else:
        message = ("#" + ticker + " " + str(
            round(float((marketdata.candle.volume * medium_price - storage_volumeRub) / 1000000), 2)) + "M₽" +
                   str(percentage_change) + "%" + '\n' +
                   "🔷 Аномальный объем" + '\n' +
                   name + '\n' +
                   "Объём: " + str(
                    round(float((marketdata.candle.volume * medium_price - storage_volumeRub) / 1000000), 2)) + "M₽ (" +
                   str(marketdata.candle.volume - storage_volume) + " лотов)" + '\n' +
                   # "Покупка: " + str(buy_percentage) + "% Продажа: " + str(sell_percentage) + "%" + '\n' +
                   # "Цена: " + str(Price_Now) + "₽" + '\n' +
                   "Не удалось определить пропорцию покупки и продажи"'\n'
                   "Изменение цены:" + '\n' +
                   "    на объеме: " + str(percentage_change) + "%" + '\n' +
                   "    за сегодня: " + str(percentage_change_today) + "%" + '\n' +
                   "Время: " + str(datetime.datetime.now().replace(microsecond=0)))

        bot.send_message(channel_id, message)
        print(message)
