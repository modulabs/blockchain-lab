import requests
import json

url = "https://api.upbit.com/v1/orderbook"

#querystring = {"markets":"markets"}

market = "KRW-BTC"
querystring = {"markets":market}

response = requests.request("GET", url, params=querystring)

#print(response.text)
res = json.loads(response.text)
#print(res)
for r in res:
    print(r)
