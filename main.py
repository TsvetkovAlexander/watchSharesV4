import asyncio

from dotenv import load_dotenv

import getNewHistoryData
import monitoringVolume

load_dotenv()


async def main():
    # Загружаем в базу новые данные за последние дни и получаем значения аномальных объемов
    dict_max_volume = await getNewHistoryData.get_history_candles()
    print(dict_max_volume)
    # Запускаем функцию мониторинга аномальных объемов
    asyncio.run(await monitoringVolume.monitoring(dict_max_volume))


if __name__ == "__main__":
    asyncio.run(main())