import requests
import resources as rs
import json

resp = requests.get('https://api.kraken.com/0/public/AssetPairs')
data = resp.json()


data = data['result']
for key, data in data.items():
    rs.addRowCsv("pairs.csv", data['wsname'])
    # print(key, data['wsname'])
# print(resp.json())
