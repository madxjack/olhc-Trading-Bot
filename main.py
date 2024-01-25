# Import WebSocket client library (and others)
import websocket
import time
import resources as rs
import json
from datetime import datetime, timedelta
import telegram as tg
import threading
import os

# Pairs tradeables https://api.kraken.com/0/public/AssetPairs

# Define WebSocket callback functions


def ws_message(ws, message):
    wsData = json.loads(message)
    if 'event' in wsData:
        return
    try:
        highPrice = wsData[1][3]
        lowPrice = wsData[1][4]
        lowPriceFloat = float(lowPrice)
        highPriceFloat = float(highPrice)
        openPrice = float(wsData[1][2])
        closePrice = float(wsData[1][5])
        pairName = wsData[3]

        if os.path.exists('bans.csv') and rs.checkBanPairOut(pairName):
            return

        if not highPriceFloat == 0 and not lowPriceFloat == 0 and not openPrice == 0:
            diffCloseHigh = rs.getPercent(openPrice, highPrice)
            diffCloseLow = rs.getPercent(openPrice, lowPrice)
            if diffCloseHigh > diffCloseLow:
                flowBum = 'UP_ACT'
                percentDiff = diffCloseHigh
            else:
                flowBum = 'DOWN_ACT'
                percentDiff = diffCloseLow

            percentDiff = round(percentDiff, 2)

            pairCrypName = pairName.split('/')[0]
            pairFiatName = pairName.split('/')[1]

            timeStart = float(wsData[1][0])
            timeStart = rs.convert_timestamp_to_datetime(timeStart)
            timeStart = timeStart + timedelta(hours=1)
            # timeStart = rs.convertDatetimetoUTC1(timeStart)
            timeStart = rs.convertDatetime_to_string(timeStart)
            timeEnd = float(wsData[1][1])
            timeEnd = rs.convert_timestamp_to_datetime(timeEnd)
            timeEnd = timeEnd + timedelta(hours=1)
            timeEnd = rs.convertDatetime_to_string(timeEnd)

            avgPrice = wsData[1][6]
            volumePair = wsData[1][7]
            volumePair = round(float(volumePair), 2)
            volume = float(wsData[1][7]) * float(avgPrice)
            volume = round(float(volume), 2)

            dateNowFilter = datetime.now() - timedelta(minutes=5)
            dateCheckFilter = datetime.strptime(timeEnd, '%d-%m-%Y %H:%M:%S')

            if percentDiff > 0 and dateNowFilter < dateCheckFilter:
                tgMessage = pairName + '\n'
                tgMessage = tgMessage + '%: ' + str(percentDiff) + '\n'
                tgMessage = tgMessage + 'ALAR: ' + flowBum + '\n'
                tgMessage = tgMessage + 'HORA_PAB: ' + str(timeStart) + '\n'
                tgMessage = tgMessage + 'HORA_FIN: ' + str(timeEnd) + '\n'
                tgMessage = tgMessage + 'VOL_' + \
                    pairCrypName + ': ' + str(volumePair) + '\n'
                tgMessage = tgMessage + 'VOL_' + \
                    pairFiatName + ': ' + str(volume) + '\n'

                if pairFiatName == 'USD':
                    tgMessage = tgMessage + 'VOL_$' + ': ' + str(volume) + '\n'
                    volumeUSD = volume
                elif pairFiatName == "JPY" or pairFiatName == "AED" or pairFiatName == 'CHF' or pairFiatName == 'CAD':
                    volumeTemp = rs.getPriceUSD(pairFiatName)
                    volumeUSD = volume / float(volumeTemp)
                    volumeUSD = round(volumeUSD, 2)
                    tgMessage = tgMessage + 'VOL_$_' + \
                        pairFiatName + ': ' + str(volumeUSD) + '\n'
                else:
                    volumeUSD = rs.getPriceUSD(pairFiatName)
                    volumeUSD = float(volumeUSD) * volume
                    volumeUSD = round(volumeUSD, 2)
                    tgMessage = tgMessage + 'VOL_$' + \
                        ': ' + str(volumeUSD) + '\n'

                tgMessage = tgMessage + 'PRICE_AVG: ' + str(avgPrice) + '\n'
                tgMessage = tgMessage + 'OPEN: ' + str(openPrice) + '\n'
                tgMessage = tgMessage + 'HIGH: ' + highPrice + '\n'
                tgMessage = tgMessage + 'LOW: ' + lowPrice + '\n'
                tgMessage = tgMessage + 'CLOSE: ' + str(closePrice) + '\n'

                if pairCrypName == 'XBT':
                    pairCrypName = 'BTC'
                elif pairFiatName == 'XBT':
                    pairFiatName = 'BTC'
                tgMessage = tgMessage + 'https://trade.kraken.com/es-es/charts/KRAKEN:' + \
                    pairCrypName + '-' + pairFiatName + '\n'
                tgMessage = tgMessage + 'https://trade.kraken.com/es-es/charts/KRAKEN:' + \
                    pairCrypName + '-' + 'USD' + '\n'

                if rs.checkFidu(pairCrypName, pairFiatName) == True and (percentDiff > 0.25) and volumeUSD > 20000:
                    tg.sendTelegram(tgMessage, 'fiat')
                    rs.banPair(pairName)
                if rs.checkVolat(pairCrypName, pairFiatName) == True and (percentDiff > 0.40) and volumeUSD > 50000:
                    tg.sendTelegram(tgMessage, 'volat')
                    rs.banPair(pairName)
                elif (percentDiff > 3 and percentDiff <= 10 and volumeUSD > 7500):
                    tg.sendTelegram(tgMessage, '3-10')
                    rs.banPair(pairName)
                elif (percentDiff > 10 and percentDiff <= 20 and volumeUSD > 3000):
                    tg.sendTelegram(tgMessage, '10-20')
                    rs.banPair(pairName)
                elif (percentDiff > 20 and percentDiff <= 50 and volumeUSD > 1000):
                    tg.sendTelegram(tgMessage, '20-50')
                    rs.banPair(pairName)
                elif (percentDiff > 50):
                    tg.sendTelegram(tgMessage, '+50')
                    rs.banPair(pairName)

    except Exception as e:
        print(e)
        tg.sendTelegramArbitrageBotOk(
            'OLHC ERR-MSG ' + str(pairName) + ' : ' + str(e))


def ws_error(ws, message):
    tg.sendTelegramArbitrageBotOk(message)
    print(message)
    try:
        tg.sendTelegramArbitrageBotOk('OLHC Iniciando nuevo thread...')
        ws_thread()
    except:
        time.wait(5)


def ws_open(ws):
    pairsList = rs.getPairList("pairs.csv")
    i = 0
    for pair in pairsList:
        ws.send(
            '{"event":"subscribe", "subscription":{"name":"ohlc", "interval":1}, "pair":' + '["' + pair + '"]}')
        # Queue 25 messages at a time
        if i % 25 == 0:
            time.sleep(1)
        i += 1


def ws_thread():
    tg.sendTelegramArbitrageBotOk('OLHC BOT: Nuevo thread iniciado...')
    ws = websocket.WebSocketApp(
        "wss://ws.kraken.com/", on_open=ws_open, on_message=ws_message,  on_error=ws_error)
    ws.run_forever(ping_interval=30, reconnect=5)
    tg.sendTelegramArbitrageBotOk('OLHC BOT: Thread finalizado.')


def mainThread():
    # Continue other (non WebSocket) tasks in the main thread
    startDate = datetime.now()
    tg.sendTelegramArbitrageBotOk("OLHC Bot On.")
    while True:
        time.sleep(1)
        nowTime = datetime.fromtimestamp(
            time.time()).strftime('%d-%m-%Y %H:%M:%S')
        print(f"Main thread: {nowTime}")

        myThreads = threading.enumerate()
        alive = False
        for thread in myThreads:
            if thread.name == 't1':
                alive = True

        if alive == False:
            tg.sendTelegramArbitrageBotOk("OLHC Bot Off. Reiniciando...")
            t1 = threading.Thread(target=ws_thread, name='t1')
            t1.start()
        else:
            nowDate = datetime.now()
            if (startDate + timedelta(minutes=60) < nowDate):
                startDate = nowDate
                tg.sendTelegramArbitrageBotOk("OLHC Bot alive.")


# Start a new thread for the WebSocket interface
if __name__ == "__main__":
    if os.path.exists('bans.csv'):
        os.remove('bans.csv')
    # _thread.start_new_thread(ws_thread, ())
    t1 = threading.Thread(target=ws_thread, name='t1')
    t2 = threading.Thread(target=mainThread, name='t2')

    t1.start()
    t2.start()

    t1.join()
    t2.join()
