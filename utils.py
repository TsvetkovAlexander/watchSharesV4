from datetime import timedelta
import datetime
from tinkoff.invest import AsyncClient, CandleInterval
import holidays
from tinkoff.invest import (
    CandleInstrument,
    SubscriptionInterval,
)


async def find_prices(figi_current, marketdata, arr_times_figi_volume, medium_price,holidays, client):
    today = datetime.datetime.now().date()
    current_time = datetime.datetime.now().time()
    start_time = datetime.datetime.combine(today, datetime.datetime.min.time()) + timedelta(hours=10)
    end_time = start_time + timedelta(minutes=1)
    elFigiVolume = [figi_current, marketdata.candle.volume, medium_price * marketdata.candle.volume]
    arr_times_figi_volume.append(elFigiVolume)
    lastPrice = await client.market_data.get_last_prices(figi=[figi_current])
    days_to_check = 20
    current_day = datetime.datetime.now().date()
    todayOpenPrice = None
    # Цикл для прохода по предыдущим дням

    for i in range(1, days_to_check + 1):  # Начинаем с 1 для вчерашнего дня:
        current_date_to_check = current_day - timedelta(days=i)
        # print("current_date_to_check",current_date_to_check)
        current_date_str = current_date_to_check.strftime('%Y-%m-%d')
        # print(holidays,"holidays")
        if current_date_str not in holidays and current_date_to_check.weekday() < 5:  # Проверка, что дата не входит в список выходных и является рабочим днем
            # print("current_date_str",current_date_str)
            todayOpenPrice = await client.market_data.get_candles(
                figi=figi_current,
                from_=datetime.datetime.now()-timedelta(days=i), to=datetime.datetime.now()-timedelta(days=i-1),
                interval=CandleInterval.CANDLE_INTERVAL_DAY
            )
        if todayOpenPrice:
            # print(lastPrice, todayOpenPrice, "lastPrice, todayOpenPrice")
            # Если свечи найдены, завершаем цикл
            return lastPrice, todayOpenPrice



# получение выходных, чтобы в эти дни не получать данные по свечам.
def get_weekend_dates():
    today = datetime.datetime.today()
    last_month = today.replace(day=1) - timedelta(days=45)
    first_day = last_month.replace(day=1)

    free_dates = []

    for ptr in holidays.RU(years=datetime.datetime.today().year).items():
        date_str = ptr[0].strftime("%Y-%m-%d")
        free_dates.append(date_str)

    while first_day <= today:
        if first_day.weekday() == 5 or first_day.weekday() == 6:  # Проверка, является ли день выходным (5 или 6 - Сб или Вс)
            free_dates.append(first_day.strftime("%Y-%m-%d"))
        first_day += timedelta(days=1)

    work_days = ['2024-01-03','2024-01-04','2024-01-05']  # массив рабочих дней
    non_working_days = [date for date in free_dates if date not in work_days]  # создаем новый список невыходных дней
    print(" non_working_days", non_working_days)
    return non_working_days

def is_holiday(day):
    holidays_list = holidays.RU(years=datetime.datetime.today().year).keys()
    if day in holidays_list or day.weekday() == 5 or day.weekday() == 6:
        return True
    else:
        return False


def cast_money(v):
    return v.units + v.nano / 1e9  # nano - 9 нулей


def compare_numbers(price_now, comparing_price):
    result = round(((price_now / comparing_price) - 1) * 100, 2)
    if result > 0:
        result = '+' + str(result)
    return result


def countVolume(arr_times_figi_volume, figi_current):
    total_sum = 0
    total_sumRub = 0
    for i in range(len(arr_times_figi_volume)):
        if arr_times_figi_volume[i][0] == figi_current:
            total_sum += arr_times_figi_volume[i][1]
            total_sumRub += arr_times_figi_volume[i][2]
    return total_sum, total_sumRub


# def search_trades_inArr():tmp_sell
#     totalVolume = 0
#     for i, el in enumerate(arrTimesDirecion):
#         if el[0] == marketdata.candle.figi:
#             tmpBuy = el[1]
#             tmpSell = el[2]
#             totalVolume = tmpBuy + tmpSell
#             print(tmpBuy, "tmpBuy")
#             print(tmpSell, "tmpSell")


# Вообще вот это лучше выделить в отдельный файл
# Список акций и их фиги для получения в стриме по мониторингу
arrInstrument = [
    CandleInstrument(
        figi="BBG000BN56Q9",  # dsky
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000RMWQD4",  # enpg
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004PYF2N3",  # poly
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000GQSVC2",  # NKNCP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000FWGSZ5",  # irkt
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000PKWCQ7",  # mrkv
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68CV8",  # vsmo
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000Q7ZZY2",  # unac
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="TCS00A106YF0",  # VKCO
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68C39",  # lsrg
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000RJL816",  # ttlk
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000BBV4M5",  # cntl
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004RVFCY3",  # mgnt
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68JR8",  # svav
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG002GHV6L9",  # spbe
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG001M2SC01",  # etln
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S685M3",  # RTKMP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # GEMC
        figi="BBG011MCM288",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # KZOSP
        figi="BBG0029SG1C1",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="TCS00A105EX7",  # WUSH
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000LNHHJ9",  # KMAZ
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG0029SFXB3",  # KZOS
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00ZHCX1X2",  # FIXP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S689R0",  # PHOR
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),

    CandleInstrument(
        figi="TCS00A106XF2",  # HNFG
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),

    CandleInstrument(
        figi="TCS2207L1061",  # HHRU
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000SK7JS5",  #
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # LNZL
        figi="BBG000PZ0833",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # ELFV
        figi="BBG000F6YPH8",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # SELG
        figi="BBG002458LF8",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # AGRO
        figi="BBG007N0Z367",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # TATNP
        figi="BBG004S68829",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # VEON-RX
        figi="BBG00R4Z2NT4",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # BLNG
        figi="BBG000VQWH86",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # PRFN
        figi="TCS00A0JNXF9",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(  # MAGN
        figi="BBG004S68507",
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004730ZJ9",  # VTBR
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00F6NKQX3",  # SMLT
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68758",  # BANE
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S683W7",  # AFLT
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG012YQ6P43",  # CIAN
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="TCS00A105NV2",  # CARM
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG008F2T3T2",  # RUAL
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00BGKYH17",  # NKHP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004730N88",  # SBER
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="TCS00A105BN4",  # GECO
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00Y3XYV94",  # MDMG
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00HY6V6H5",  # GTRK
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68CP5",  # MVID
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S686N0",  # BANEP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00172J7S9",  # OKEY
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68B31",  # ALRS
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000VG1034",  # MRKP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000R04X57",  # FLOT
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000MZL2S9",  # PMSBP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004RVFFC0",  # TATN
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00JXPFBN0",  # FIVE
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68DD6",  # MSTT
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68598",  # MTLR
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="TCS10A0JNAB6",  # ABIO
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG008HD3V85",  # UWGN
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S688G4",  # AKRN
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004730RP0",  # GAZP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000V07CB8",  # DVEC
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG0047315Y7",  # SBERP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S682Z6",  # RTKM
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG0063FKTD9",  # LENT
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG0019K04R5",  # LIFE
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000QJW156",  # BSPB
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S681W1",  # MTSS
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="RU000A106T36",  # ASTR
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000RG4ZQ4",  # TGKN
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00475KHX6",  # TRNFP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000LWNRP3",  # RKKE
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000NLC9Z6",  # LSNG
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00QKJSX05",  # RENI
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000VH7TZ8",  # MRKC
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="TCS00A103X66",  # POSI
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00475JZZ6",  # FEES
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000NLB2G3",  # KROT
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG002B9MYC1",  # KAZT
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000MZL0Y6",  # PMSB
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG002GHV6L9",  # spbe
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S684M6",  # SIBN
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG002B298N6",  # YAKG
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000Q7GG57",  # TGKB
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000DBD6F6",  # KLSB
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000RP8V70",  # CHMK
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00F9XX7H4",  # RNFT
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S687G6",  # MSRS
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000TJ6F42",  # MRKZ
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000K3STR7",  # APTK
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG005D1WCQ1",  # QIWI
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68473",  # IRAO
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00475K2X9",  # HYDR
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG002BCQK67",  # NSVZ
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S681B4",  # NLMK
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000TY1CD1",  # BELU
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000RTHVK7",  # GCHE
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000SR0YS4",  # LNZLP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00QPYJ5H0",  # TCSG
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S681M2",  # SNGSP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG006L8G4H1",  # YNDX
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),

    CandleInstrument(
        figi="BBG003LYCMB1",  # SFIN
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000QF1Q17",  # FESH
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68696",  # RASP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00475KKY8",  # NVTK
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG002YFXL29",  # UNKL
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000GQSRR5",  # NKNC
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000W325F7",  # AQUA
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000BX7DH0",  # VRSB
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG0100R9963",  # SGZH
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000NLCCM3",  # LSNGP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004731489",  # GMKN
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),

    CandleInstrument(
        figi="BBG004730JJ5",  # MOEX
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S686W0",  # UPRO
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000VJMH65",  # MRKS
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004Z2RGW8",  # ROLO
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S687W8",  # MSNG
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68614",  # AFKS
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000R607Y3",  # PLZL
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00Y91R9T3",  # OZON
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004731032",  # LKOH/
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000RK52V1",  # OGKB
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000VFX6Y4",  # GLTR
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG002B9T6Y1",  # KAZTP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68BR5",  # NMTP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000QFH687",  # TGKA
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG0047315D0",  # SNGS
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),

    CandleInstrument(
        figi="BBG009GSYN76",  # CBOM
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000RJWGC4",  # AMEZ
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000Q7GJ60",  # TGKBP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),

    CandleInstrument(
        figi="BBG002W2FT69",  # ABRD
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),

    CandleInstrument(
        figi="BBG0027F0Y27",  # CNTLP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68BH6",  # PIKK
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004731354",  # ROSN
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="TCS00A1002V2",  # EUTR
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004S68FR6",  # MTLRP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG004TC84Z8",  # TRMK
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="TCS00A0ZZBC2",  # SOFL/
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000VKG4R5",  # MRKU/
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG000C7P5M7",  # MRKY
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG002B2J5X0",  # KRKNP
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
    CandleInstrument(
        figi="BBG00475K6C3",  # CHMF
        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
    ),
]

arrTradeInstrument = [  # Список акций и их фиги для получения в стриме по мониторингу
    CandleInstrument(
        figi="BBG000BN56Q9",  # dsky
    ),
    CandleInstrument(
        figi="BBG000RMWQD4",  # enpg
    ),
    CandleInstrument(
        figi="BBG004PYF2N3",  # poly
    ),
    CandleInstrument(
        figi="BBG000GQSVC2",  # NKNCP
    ),
    CandleInstrument(
        figi="BBG000FWGSZ5",  # irkt
    ),
    CandleInstrument(
        figi="BBG000PKWCQ7",  # mrkv
    ),
    CandleInstrument(
        figi="BBG004S68CV8",  # vsmo
    ),
    CandleInstrument(
        figi="BBG000Q7ZZY2",  # unac
    ),
    CandleInstrument(
        figi="BBG004S68C39",  # lsrg
    ),
    CandleInstrument(
        figi="TCS00A106YF0",  # VKCO
    ),
    CandleInstrument(
        figi="BBG000RJL816",  # ttlk
    ),
    CandleInstrument(
        figi="BBG000BBV4M5",  # cntl
    ),
    CandleInstrument(
        figi="BBG004RVFCY3",  # mgnt
    ),
    CandleInstrument(
        figi="BBG004S68JR8",  # svav
    ),
    CandleInstrument(
        figi="BBG002GHV6L9",  # spbe
    ),
    CandleInstrument(
        figi="BBG001M2SC01",  # etln
    ),
    CandleInstrument(
        figi="BBG004S685M3",  # RTKMP
    ),
    CandleInstrument(  # GEMC
        figi="BBG011MCM288",
    ),
    CandleInstrument(  # KZOSP
        figi="BBG0029SG1C1",
    ),
    CandleInstrument(
        figi="TCS00A105EX7",  # WUSH
    ),
    CandleInstrument(
        figi="BBG000LNHHJ9",  # KMAZ
    ),
    CandleInstrument(
        figi="BBG0029SFXB3",  # KZOS
    ),
    CandleInstrument(
        figi="BBG00ZHCX1X2",  # FIXP
    ),
    CandleInstrument(
        figi="BBG004S689R0",  # PHOR
    ),
    CandleInstrument(
        figi="TCS00A106XF2",  # HNFG
    ),
    CandleInstrument(
        figi="TCS2207L1061",  # HHRU
    ),
    CandleInstrument(
        figi="BBG000SK7JS5",  #
    ),
    CandleInstrument(  # LNZL
        figi="BBG000PZ0833",
    ),
    CandleInstrument(  # ELFV
        figi="BBG000F6YPH8",
    ),
    CandleInstrument(  # SELG
        figi="BBG002458LF8",
    ),
    CandleInstrument(  # AGRO
        figi="BBG007N0Z367",
    ),
    CandleInstrument(  # TATNP
        figi="BBG004S68829",
    ),
    CandleInstrument(  # VEON-RX
        figi="BBG00R4Z2NT4",
    ),
    CandleInstrument(  # BLNG
        figi="BBG000VQWH86",
    ),
    CandleInstrument(  # PRFN
        figi="TCS00A0JNXF9",
    ),
    CandleInstrument(  # MAGN
        figi="BBG004S68507",
    ),
    CandleInstrument(
        figi="BBG004730ZJ9",  # VTBR
    ),
    CandleInstrument(
        figi="BBG00F6NKQX3",  # SMLT
    ),
    CandleInstrument(
        figi="BBG004S68758",  # BANE
    ),
    CandleInstrument(
        figi="BBG004S683W7",  # AFLT
    ),
    CandleInstrument(
        figi="BBG012YQ6P43",  # CIAN
    ),
    CandleInstrument(
        figi="TCS00A105NV2",  # CARM
    ),
    CandleInstrument(
        figi="BBG008F2T3T2",  # RUAL
    ),
    CandleInstrument(
        figi="BBG00BGKYH17",  # NKHP
    ),
    CandleInstrument(
        figi="BBG004730N88",  # SBER
    ),
    CandleInstrument(
        figi="TCS00A105BN4",  # GECO
    ),
    CandleInstrument(
        figi="BBG00Y3XYV94",  # MDMG
    ),
    CandleInstrument(
        figi="BBG00HY6V6H5",  # GTRK
    ),
    CandleInstrument(
        figi="BBG004S68CP5",  # MVID
    ),
    CandleInstrument(
        figi="BBG004S686N0",  # BANEP
    ),
    CandleInstrument(
        figi="BBG00172J7S9",  # OKEY
    ),
    CandleInstrument(
        figi="BBG004S68B31",  # ALRS
    ),
    CandleInstrument(
        figi="BBG000VG1034",  # MRKP
    ),
    CandleInstrument(
        figi="BBG000R04X57",  # FLOT
    ),
    CandleInstrument(
        figi="BBG000MZL2S9",  # PMSBP
    ),
    CandleInstrument(
        figi="BBG004RVFFC0",  # TATN
    ),
    CandleInstrument(
        figi="BBG00JXPFBN0",  # FIVE
    ),
    CandleInstrument(
        figi="BBG004S68DD6",  # MSTT
    ),
    CandleInstrument(
        figi="BBG004S68598",  # MTLR
    ),
    CandleInstrument(
        figi="TCS10A0JNAB6",  # ABIO
    ),
    CandleInstrument(
        figi="BBG008HD3V85",  # UWGN
    ),
    CandleInstrument(
        figi="BBG004S688G4",  # AKRN
    ),
    CandleInstrument(
        figi="BBG004730RP0",  # GAZP
    ),
    CandleInstrument(
        figi="BBG000V07CB8",  # DVEC
    ),
    CandleInstrument(
        figi="BBG0047315Y7",  # SBERP
    ),
    CandleInstrument(
        figi="BBG004S682Z6",  # RTKM
    ),
    CandleInstrument(
        figi="BBG0063FKTD9",  # LENT
    ),
    CandleInstrument(
        figi="BBG0019K04R5",  # LIFE
    ),
    CandleInstrument(
        figi="BBG000QJW156",  # BSPB
    ),
    CandleInstrument(
        figi="BBG004S681W1",  # MTSS
    ),
    CandleInstrument(
        figi="RU000A106T36",  # ASTR
    ),
    CandleInstrument(
        figi="BBG000RG4ZQ4",  # TGKN
    ),
    CandleInstrument(
        figi="BBG00475KHX6",  # TRNFP
    ),
    CandleInstrument(
        figi="BBG000LWNRP3",  # RKKE
    ),
    CandleInstrument(
        figi="BBG000NLC9Z6",  # LSNG
    ),
    CandleInstrument(
        figi="BBG00QKJSX05",  # RENI
    ),
    CandleInstrument(
        figi="BBG000VH7TZ8",  # MRKC
    ),
    CandleInstrument(
        figi="TCS00A103X66",  # POSI
    ),
    CandleInstrument(
        figi="BBG00475JZZ6",  # FEES
    ),
    CandleInstrument(
        figi="BBG000NLB2G3",  # KROT
    ),
    CandleInstrument(
        figi="BBG002B9MYC1",  # KAZT
    ),
    CandleInstrument(
        figi="BBG000MZL0Y6",  # PMSB
    ),
    CandleInstrument(
        figi="BBG002GHV6L9",  # spbe
    ),
    CandleInstrument(
        figi="BBG004S684M6",  # SIBN
    ),
    CandleInstrument(
        figi="BBG002B298N6",  # YAKG
    ),
    CandleInstrument(
        figi="BBG000Q7GG57",  # TGKB
    ),
    CandleInstrument(
        figi="BBG000DBD6F6",  # KLSB

    ),
    CandleInstrument(
        figi="BBG000RP8V70",  # CHMK
    ),
    CandleInstrument(
        figi="BBG00F9XX7H4",  # RNFT
    ),
    CandleInstrument(
        figi="BBG004S687G6",  # MSRS
    ),
    CandleInstrument(
        figi="BBG000TJ6F42",  # MRKZ
    ),
    CandleInstrument(
        figi="BBG000K3STR7",  # APTK
    ),
    CandleInstrument(
        figi="BBG005D1WCQ1",  # QIWI
    ),
    CandleInstrument(
        figi="BBG004S68473",  # IRAO
    ),
    CandleInstrument(
        figi="BBG00475K2X9",  # HYDR
    ),
    CandleInstrument(
        figi="BBG002BCQK67",  # NSVZ
    ),
    CandleInstrument(
        figi="BBG004S681B4",  # NLMK
    ),
    CandleInstrument(
        figi="BBG000TY1CD1",  # BELU
    ),
    CandleInstrument(
        figi="BBG000RTHVK7",  # GCHE
    ),
    CandleInstrument(
        figi="BBG000SR0YS4",  # LNZLP
    ),
    CandleInstrument(
        figi="BBG00QPYJ5H0",  # TCSG
    ),
    CandleInstrument(
        figi="BBG004S681M2",  # SNGSP
    ),
    CandleInstrument(
        figi="BBG006L8G4H1",  # YNDX
    ),
    CandleInstrument(
        figi="BBG003LYCMB1",  # SFIN
    ),
    CandleInstrument(
        figi="BBG000QF1Q17",  # FESH
    ),
    CandleInstrument(
        figi="BBG004S68696",  # RASP
    ),
    CandleInstrument(
        figi="BBG00475KKY8",  # NVTK
    ),
    CandleInstrument(
        figi="BBG002YFXL29",  # UNKL
    ),
    CandleInstrument(
        figi="BBG000GQSRR5",  # NKNC
    ),
    CandleInstrument(
        figi="BBG000W325F7",  # AQUA
    ),
    CandleInstrument(
        figi="BBG000BX7DH0",  # VRSB
    ),
    CandleInstrument(
        figi="BBG0100R9963",  # SGZH
    ),
    CandleInstrument(
        figi="BBG000NLCCM3",  # LSNGP
    ),
    CandleInstrument(
        figi="BBG004731489",  # GMKN
    ),

    CandleInstrument(
        figi="BBG004730JJ5",  # MOEX
    ),
    CandleInstrument(
        figi="BBG004S686W0",  # UPRO
    ),
    CandleInstrument(
        figi="BBG000VJMH65",  # MRKS
    ),
    CandleInstrument(
        figi="BBG004Z2RGW8",  # ROLO
    ),
    CandleInstrument(
        figi="BBG004S687W8",  # MSNG
    ),
    CandleInstrument(
        figi="BBG004S68614",  # AFKS
    ),
    CandleInstrument(
        figi="BBG000R607Y3",  # PLZL
    ),
    CandleInstrument(
        figi="BBG00Y91R9T3",  # OZON
    ),
    CandleInstrument(
        figi="BBG004731032",  # LKOH/
    ),
    CandleInstrument(
        figi="BBG000RK52V1",  # OGKB
    ),
    CandleInstrument(
        figi="BBG000VFX6Y4",  # GLTR
    ),
    CandleInstrument(
        figi="BBG002B9T6Y1",  # KAZTP
    ),
    CandleInstrument(
        figi="BBG004S68BR5",  # NMTP
    ),
    CandleInstrument(
        figi="BBG000QFH687",  # TGKA
    ),
    CandleInstrument(
        figi="BBG0047315D0",  # SNGS
    ),
    CandleInstrument(
        figi="BBG009GSYN76",  # CBOM
    ),
    CandleInstrument(
        figi="BBG000RJWGC4",  # AMEZ
    ),
    CandleInstrument(
        figi="BBG000Q7GJ60",  # TGKBP
    ),

    CandleInstrument(
        figi="BBG002W2FT69",  # ABRD
    ),
    CandleInstrument(
        figi="BBG0027F0Y27",  # CNTLP
    ),
    CandleInstrument(
        figi="BBG004S68BH6",  # PIKK
    ),
    CandleInstrument(
        figi="BBG004731354",  # ROSN
    ),
    CandleInstrument(
        figi="TCS00A1002V2",  # EUTR
    ),
    CandleInstrument(
        figi="BBG004S68FR6",  # MTLRP
    ),
    CandleInstrument(
        figi="BBG004TC84Z8",  # TRMK
    ),
    CandleInstrument(
        figi="TCS00A0ZZBC2",  # SOFL/
    ),
    CandleInstrument(
        figi="BBG000VKG4R5",  # MRKU/
    ),
    CandleInstrument(
        figi="BBG000C7P5M7",  # MRKY
    ),
    CandleInstrument(
        figi="BBG002B2J5X0",  # KRKNP
    ),
    CandleInstrument(
        figi="BBG00475K6C3",  # CHMF
    ),
]