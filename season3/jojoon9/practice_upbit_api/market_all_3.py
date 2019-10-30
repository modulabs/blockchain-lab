"""
import requests
import json
url = "https://api.upbit.com/v1/market/all"

response = requests.request("GET", url)

info_list = json.loads(response.text)
"""

import market_all as ma

info_list = ma.market_all()

coins = []
for d in info_list:
    if not d['korean_name'] in coins:
        coins.append(d['korean_name'])

print("Total : {}".format(len(info_list)))
print("Types : {}".format(len(coins)))

for i in coins:
    print(i, end=" ")
