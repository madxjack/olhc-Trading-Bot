import csv
import requests
from datetime import datetime, timedelta
from dateutil import tz
import pandas as pd

def addRowCsv(csvFilename, toAdd):
    with open(csvFilename, 'a', newline='')  as writeFile:
        writer = csv.writer(writeFile, delimiter=' ', escapechar=' ', quoting=csv.QUOTE_NONE)
        writer.writerow([toAdd])

def getPairList(name):
    listPairs = []
    with open(name, 'r') as file:
        reader = csv.reader(file, delimiter=' ')
        for pair in reader:
            newSymbol = str(pair)[2:-2]
            listPairs.append(newSymbol)

    return listPairs

def getPercent(lowNumber, highNumber):
    lowNumber = float(lowNumber)
    highNumber = float(highNumber)
    result = float(((highNumber - lowNumber) * 100 / lowNumber))

    return abs(result)

def getPriceUSD(pair):
    usd = "USD"

    if pair == "JPY" or pair == "AED" or pair == 'CHF' or  pair == 'CAD':
        fullPair = usd + pair
    else:
        fullPair = pair + usd
    response = requests.get(f"https://api.kraken.com/0/public/Ticker?pair={fullPair}")
    response = response.json()
    response = response['result']
    for response in response.items():
        price = response[1]['a'][0]

    return price

def banPair(pair):
    datetimeBinance = datetime.now()
    dateBum = datetime.strftime(datetimeBinance, '%Y-%m-%d %H:%M:%S')
    bum = pair + ',' + dateBum
    # print(f'Pair baneado: {bum}')
    addRowCsv('bans.csv', bum)

def checkBanPairOut(pair):
    nowDate = datetime.now()
    check = False
    pairsOut = []
    bans = pd.read_csv('bans.csv', names=['name', 'date'])
    if bans.empty:
        check = False
    else:
        if pair in bans.values:
            rowBan = bans[bans['name'] == pair].index
            for row in rowBan:
                dateToApp = bans.loc[row, 'date']
                dateToApp = datetime.strptime(dateToApp, '%Y-%m-%d  %H:%M:%S')
                dateToApp = dateToApp + timedelta(seconds=10)
                pairsOut.append([row, dateToApp]) 

            # print(f'Date Pair banned: {dictDate}')
            # print(f'Date finish ban: {dateBan}')
            for pairOut in pairsOut:
                if nowDate < pairOut[1]:
                    check = True
                    return check
                else:
                    bans = bans.drop(pairOut[0])
            bans.to_csv('bans.csv', header=False, index=False)
            # print(f'Pair cleaned. {listBans}')
    return check
    
def convert_timestamp_to_datetime(ts):
    dt = datetime.fromtimestamp(ts)
    return dt
def convertDatetimetoUTC1(dt):
    from_zone = tz.gettz()
    to_zone = tz.gettz('Europe/Spain')
    dt = dt.replace(tzinfo=from_zone)
    dt_spain = dt.astimezone(to_zone)

    return dt_spain

def convertDatetime_to_string(dt):
    dt = dt.strftime('%d-%m-%Y %H:%M:%S')
    return dt

def checkFidu(fiat1, fiat2):
    fidu1, fidu2, ok = False, False, False
    fiduPairs = getPairList('pairs_fiat.csv')

    for pair in fiduPairs:   
        if pair == fiat1:
            fidu1 = True
        if pair == fiat2:
            fidu2 = True
    
    if (fidu1 and fidu2) == True:
        ok = True
    return ok

def checkVolat(volat1, volat2):
    pair1, pair2, ok = False, False, False
    volaPairs = getPairList('pairs_volatilidad.csv')
    fiduPairs = getPairList('pairs_fiat.csv')

    for pair in volaPairs:   
        if pair == volat1:
            pair1 = True
            for fpair in fiduPairs:
                if fpair == volat2:
                    pair2 = True
    
    if (pair1 and pair2) == True:
        ok = True
    return ok

