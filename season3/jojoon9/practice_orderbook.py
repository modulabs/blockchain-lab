import requests
import json

def upbit_orderbook(market):
    upbit_url = "https://api.upbit.com/v1/orderbook"
    querystring = {"markets":market}
    response = requests.request("GET", upbit_url, params=querystring)

    res = json.loads(response.text)
    return res

print(upbit_orderbook('KRW-EOS'))
print(type('KRW-EOS'))
