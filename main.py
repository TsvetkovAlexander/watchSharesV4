import asyncio
import time
from datetime import datetime

from dotenv import load_dotenv

import getNewHistoryData
import monitoringVolume

load_dotenv()


async def main():
    # Загружаем в базу новые данные за последние дни и получаем значения аномальных объемов
    try:
        dict_max_volume = await getNewHistoryData.get_history_candles()
    except Exception as error:
        print('An exception occurred: {}'.format(error))
        log_file = open("getNewHistoryData.log", "a")
        log_file.write("{} - {}\n".format(str(datetime.now()), str(error)))
        log_file.close()

    print(dict_max_volume)
    # Запускаем функцию мониторинга аномальных объемов
    while True:
        try:
            asyncio.run(await monitoringVolume.monitoring(dict_max_volume))
        except Exception as error:
            print('An exception occurred: {}'.format(error))
            log_file = open("monitoringVolume.log", "a")
            log_file.write("{} - {}\n".format(str(datetime.now()), str(error)))
            log_file.close()

            time.sleep(5)
            continue


if __name__ == "__main__":
    asyncio.run(main())


  # async def checkMonitoring(dict_max_volume):
  #       while True:
  #           try:
  #               asyncio.run(await monitoringVolume.monitoring(dict_max_volume))
  #           except Exception as error:
  #               print('An exception occurred: {}'.format(error))
  #               log_file = open("monitoringVolume.log", "a")
  #               log_file.write("{} - {}\n".format(str(datetime.now()), str(error)))
  #               log_file.close()
  #
  #               time.sleep(5)
  #               continue
  #   # Загружаем в базу новые данные за последние дни и получаем значения аномальных объемов
  #   while True:
  #       try:
  #           dict_max_volume = await getNewHistoryData.get_history_candles()
  #           print(dict_max_volume)
  #           checkMonitoring(dict_max_volume)
  #       except Exception as error:
  #           print('An exception occurred: {}'.format(error))
  #           log_file = open("monitoringVolume.log", "a")
  #           log_file.write("{} - {}\n".format(str(datetime.now()), str(error)))
  #           log_file.close()
  #
  #           time.sleep(20)
  #           continue