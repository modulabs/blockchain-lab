import requests
import json

def market_all():
    url = "https://api.upbit.com/v1/market/all"
    response = requests.request("GET", url)
#    print(response.text)
#    return response.text
    return json.loads(response.text)
