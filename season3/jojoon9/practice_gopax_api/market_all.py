import requests
import json

#GET /trading-pairs

def market_all():
    url = "https://api.gopax.co.kr/trading-pairs"
    response = requests.request("GET", url)
#    print(response.text)
#    return response.text
    return json.loads(response.text)

#print(market_all())
for m in market_all():
#    print(m)
#    print(m["name"])
#    print(type(m["name"]))
#    print(m['name'].split('-'))
    print("{}-{}".format(m['name'].split('-')[1], m['name'].split('-')[0]))
