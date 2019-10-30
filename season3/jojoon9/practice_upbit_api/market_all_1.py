"""
import requests
import json
url = "https://api.upbit.com/v1/market/all"

response = requests.request("GET", url)

print(response.text)
"""

import market_all as ma

info_list = ma.market_all()

#print(type(info_list))
print(info_list)
