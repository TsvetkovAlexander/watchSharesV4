from datetime import datetime, date, time, timezone, timedelta
import holidays
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

ru_holidays = holidays.country_holidays('RU')
def get_weekend_dates(): # получение выходных, чтобы в эти дни не получать данные по свечам.
    today = datetime.today()
    last_month = today.replace(day=1) -timedelta(days=45)
    first_day = last_month.replace(day=1)

    FreeDates = []
    for ptr in holidays.RU(years=datetime.today().year).items():
        date_str = ptr[0].strftime("%Y-%m-%d")
        FreeDates.append(date_str)
    while first_day <= today:
        if first_day.weekday() == 5 or first_day.weekday() == 6:  # Проверка, является ли день выходным (5 или 6 - Сб или Вс)
            FreeDates.append(first_day.strftime("%Y-%m-%d"))
        first_day += timedelta(days=1)

    return FreeDates
def search_trades_inArr():
        totalVolume=0
        for i, el in enumerate(arrTimesDirecion):
            if el[0] == marketdata.candle.figi:
                tmpBuy = el[1]
                tmpSell = el[2]
                totalVolume = tmpBuy + tmpSell
                print(tmpBuy, "tmpBuy")
                print(tmpSell, "tmpSell")

arrInstrument= [  # Cписок акций и их фиги для получения в стриме по мониторингу
                    CandleInstrument(
                        figi="BBG000BN56Q9", #dsky
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000RMWQD4",# enpg
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004PYF2N3",# poly
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000GQSVC2", #NKNCP
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000FWGSZ5", #irkt
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000PKWCQ7", #mrkv
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S68CV8", #vsmo
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000Q7ZZY2", #unac
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S68C39", #lsrg
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000RJL816", #ttlk
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000BBV4M5", #cntl
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004RVFCY3", #mgnt
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S68JR8", #svav
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG002GHV6L9", #spbe
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG001M2SC01", #etln
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S685M3", #RTKMP
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG011MCM288",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG0029SG1C1",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="TCS00A105EX7",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000LNHHJ9",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG0029SFXB3",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00ZHCX1X2",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00178PGX3",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S689R0",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="TCS2207L1061",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000SK7JS5",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000PZ0833",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000F6YPH8",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG002458LF8",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG007N0Z367",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S68829",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00R4Z2NT4",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000VQWH86",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="TCS00A0JNXF9",
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S68507",  # dsky
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004730ZJ9",  # enpg
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00F6NKQX3",  # poly
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S68758",  # NKNCP
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S683W7",  # irkt
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG012YQ6P43",  # mrkv
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="TCS00A105NV2",  # vsmo
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG008F2T3T2",  # unac
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00BGKYH17",  # lsrg
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004730N88",  # ttlk
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="TCS00A105BN4",  # cntl
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00Y3XYV94",  # mgnt
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00HY6V6H5",  # svav
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S68CP5",  # spbe
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S686N0",  # etln
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00172J7S9",  # RTKMP
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S68B31",  # dsky
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000VG1034",  # enpg
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000R04X57",  # poly
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000MZL2S9",  # NKNCP
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004RVFFC0",  # irkt
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00JXPFBN0",  # mrkv
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S68DD6",  # vsmo
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S68598",  # unac
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG008HD3V85",  # lsrg
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S688G4",  # ttlk
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004730RP0",  # cntl
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000V07CB8",  # mgnt
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG0047315Y7",  # svav
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S682Z6",  # spbe
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG0063FKTD9",  # etln
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG0019K04R5",  # RTKMP
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000QJW156",  # dsky
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG004S681W1",  # enpg
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000RG4ZQ4",  # poly
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00475KHX6",  # NKNCP
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000LWNRP3",  # irkt
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000NLC9Z6",  # mrkv
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG00QKJSX05",  # vsmo
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="BBG000VH7TZ8",  # unac
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    CandleInstrument(
                        figi="TCS00A103X66",  # lsrg
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    ),
                    # CandleInstrument(
                    #     figi="BBG000RJL816",  # ttlk
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG000BBV4M5",  # cntl
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG004RVFCY3",  # mgnt
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG004S68JR8",  # svav
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG002GHV6L9",  # spbe
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG001M2SC01",  # etln
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG004S685M3",  # RTKMP
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                ]



arrTradeInstrument= [  # Cписок акций и их фиги для получения в стриме по мониторингу
                    CandleInstrument(
                        figi="BBG000BN56Q9", #dsky
                    ),
                    CandleInstrument(
                        figi="BBG000RMWQD4",# enpg
                                   ),
                    CandleInstrument(
                        figi="BBG004PYF2N3",# poly
                                         ),
                    CandleInstrument(
                        figi="BBG000GQSVC2", #NKNCP
                                       ),
                    CandleInstrument(
                        figi="BBG000FWGSZ5", #irkt
                                          ),
                    CandleInstrument(
                        figi="BBG000PKWCQ7", #mrkv
                                      ),
                    CandleInstrument(
                        figi="BBG004S68CV8", #vsmo
                                        ),
                    CandleInstrument(
                        figi="BBG000Q7ZZY2", #unac
                                      ),
                    CandleInstrument(
                        figi="BBG004S68C39", #lsrg
                                         ),
                    CandleInstrument(
                        figi="BBG000RJL816", #ttlk
                                        ),
                    CandleInstrument(
                        figi="BBG000BBV4M5", #cntl
                                         ),
                    CandleInstrument(
                        figi="BBG004RVFCY3", #mgnt
                                        ),
                    CandleInstrument(
                        figi="BBG004S68JR8", #svav
                                       ),
                    CandleInstrument(
                        figi="BBG002GHV6L9", #spbe
                                         ),
                    CandleInstrument(
                        figi="BBG001M2SC01", #etln
                                    ),
                    CandleInstrument(
                        figi="BBG004S685M3", #RTKMP
                                    ),
                    CandleInstrument(
                        figi="BBG011MCM288",
                                          ),
                    CandleInstrument(
                        figi="BBG0029SG1C1",
                                    ),
                    CandleInstrument(
                        figi="TCS00A105EX7",
                                       ),
                    CandleInstrument(
                        figi="BBG000LNHHJ9",
                                   ),
                    CandleInstrument(
                        figi="BBG0029SFXB3",
                                     ),
                    CandleInstrument(
                        figi="BBG00ZHCX1X2",
                                 ),
                    CandleInstrument(
                        figi="BBG00178PGX3",
                                         ),
                    CandleInstrument(
                        figi="BBG004S689R0",
                                           ),
                    CandleInstrument(
                        figi="TCS2207L1061",
                                           ),
                    CandleInstrument(
                        figi="BBG000SK7JS5",
                                           ),
                    CandleInstrument(
                        figi="BBG000PZ0833",
                                           ),
                    CandleInstrument(
                        figi="BBG000F6YPH8",
                                          ),
                    CandleInstrument(
                        figi="BBG002458LF8",
                                            ),
                    CandleInstrument(
                        figi="BBG007N0Z367",
                                            ),
                    CandleInstrument(
                        figi="BBG004S68829",
                                           ),
                    CandleInstrument(
                        figi="BBG00R4Z2NT4",
                                            ),
                    CandleInstrument(
                        figi="BBG000VQWH86",
                                          ),
                    CandleInstrument(
                        figi="TCS00A0JNXF9",
                                            ),
                    CandleInstrument(
                        figi="BBG004S68507",  # dsky
                                            ),
                    CandleInstrument(
                        figi="BBG004730ZJ9",  # enpg
                                            ),
                    CandleInstrument(
                        figi="BBG00F6NKQX3",  # poly
                                           ),
                    CandleInstrument(
                        figi="BBG004S68758",  # NKNCP
                                           ),
                    CandleInstrument(
                        figi="BBG004S683W7",  # irkt
                                           ),
                    CandleInstrument(
                        figi="BBG012YQ6P43",  # mrkv
                                           ),
                    CandleInstrument(
                        figi="TCS00A105NV2",  # vsmo
                                         ),
                    CandleInstrument(
                        figi="BBG008F2T3T2",  # unac
                                            ),
                    CandleInstrument(
                        figi="BBG00BGKYH17",  # lsrg
                                          ),
                    CandleInstrument(
                        figi="BBG004730N88",  # ttlk
                                          ),
                    CandleInstrument(
                        figi="TCS00A105BN4",  # cntl
                                            ),
                    CandleInstrument(
                        figi="BBG00Y3XYV94",  # mgnt
                                          ),
                    CandleInstrument(
                        figi="BBG00HY6V6H5",  # svav
                                            ),
                    CandleInstrument(
                        figi="BBG004S68CP5",  # spbe
                                          ),
                    CandleInstrument(
                        figi="BBG004S686N0",  # etln
                                         ),
                    CandleInstrument(
                        figi="BBG00172J7S9",  # RTKMP
                                          ),
                    CandleInstrument(
                        figi="BBG004S68B31",  # dsky
                              ),
                    CandleInstrument(
                        figi="BBG000VG1034",  # enpg
                                   ),
                    CandleInstrument(
                        figi="BBG000R04X57",  # poly
                                          ),
                    CandleInstrument(
                        figi="BBG000MZL2S9",  # NKNCP
                                      ),
                    CandleInstrument(
                        figi="BBG004RVFFC0",  # irkt
                                      ),
                    CandleInstrument(
                        figi="BBG00JXPFBN0",  # mrkv
                                      ),
                    CandleInstrument(
                        figi="BBG004S68DD6",  # vsmo
                                        ),
                    CandleInstrument(
                        figi="BBG004S68598",  # unac
                                     ),
                    CandleInstrument(
                        figi="BBG008HD3V85",  # lsrg
                                            ),
                    CandleInstrument(
                        figi="BBG004S688G4",  # ttlk
                                        ),
                    CandleInstrument(
                        figi="BBG004730RP0",  # cntl
                                           ),
                    CandleInstrument(
                        figi="BBG000V07CB8",  # mgnt
                                         ),
                    CandleInstrument(
                        figi="BBG0047315Y7",  # svav
                                ),
                    CandleInstrument(
                        figi="BBG004S682Z6",  # spbe
                                         ),
                    CandleInstrument(
                        figi="BBG0063FKTD9",  # etln
                                      ),
                    CandleInstrument(
                        figi="BBG0019K04R5",  # RTKMP
                                    ),
                    CandleInstrument(
                        figi="BBG000QJW156",  # dsky
                                     ),
                    CandleInstrument(
                        figi="BBG004S681W1",  # enpg
                                  ),
                    CandleInstrument(
                        figi="BBG000RG4ZQ4",  # poly
                                 ),
                    CandleInstrument(
                        figi="BBG00475KHX6",  # NKNCP
                                    ),
                    CandleInstrument(
                        figi="BBG000LWNRP3",  # irkt
                              ),
                    CandleInstrument(
                        figi="BBG000NLC9Z6",  # mrkv
                                 ),
                    CandleInstrument(
                        figi="BBG00QKJSX05",  # vsmo
                                         ),
                    CandleInstrument(
                        figi="BBG000VH7TZ8",  # unac
                             ),
                    CandleInstrument(
                        figi="TCS00A103X66",  # lsrg
                                           ),
                    # CandleInstrument(
                    #     figi="BBG000RJL816",  # ttlk
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG000BBV4M5",  # cntl
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG004RVFCY3",  # mgnt
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG004S68JR8",  # svav
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG002GHV6L9",  # spbe
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG001M2SC01",  # etln
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                    # CandleInstrument(
                    #     figi="BBG004S685M3",  # RTKMP
                    #     interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE,
                    # ),
                ]
