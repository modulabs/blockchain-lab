"""
import requests
import json
url = "https://api.upbit.com/v1/market/all"

response = requests.request("GET", url)

info_list = json.loads(response.text)
"""

import market_all as ma

info_list = ma.market_all()

btcs = []
for d in info_list:
    if d["korean_name"] == "비트코인":
        btcs.append(d)

for btc in btcs:
    print(btc)
