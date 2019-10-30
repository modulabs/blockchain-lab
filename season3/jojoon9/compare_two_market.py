import requests
import json

"""
def gopax_markets():
    url = "https://api.gopax.co.kr/trading-pairs"
    response = requests.request("GET", url)

    markets_info = json.loads(response.text)

    markets_name = []
    for market_info in markets_info:
        markets_name.append("{}-{}".format(market_info['name'].split('-')[1],
                                           market_info['name'].split('-')[0]))

    return markets_name

def upbit_markets():
    url = "https://api.upbit.com/v1/market/all"
    response = requests.request("GET", url)

    markets_info = json.loads(response.text)

    markets_name = []
    for market_info in markets_info:
        markets_name.append(market_info['market'])

    return markets_name

gopax_markets_list = gopax_markets()
upbit_markets_list = upbit_markets()
#print(gopax_markets_list)
#print(upbit_markets_list)
"""

def markets(url):
    response = requests.request("GET", url)

    markets_info = json.loads(response.text)

    markets_name = []

    if "gopax" in url:
        for market_info in markets_info:
            markets_name.append("{}-{}".format(market_info['name'].split('-')[1],
                                               market_info['name'].split('-')[0]))
    elif "upbit" in url:
        for market_info in markets_info:
            markets_name.append(market_info['market'])

    return markets_name

gopax_url = "https://api.gopax.co.kr/trading-pairs"
upbit_url = "https://api.upbit.com/v1/market/all"

gopax_markets_list = markets(gopax_url)
upbit_markets_list = markets(upbit_url)

intersection = list(set(gopax_markets_list) & set(upbit_markets_list))
print("Intersection market list : {}".format(intersection))

KRWs = []
BTCs = []

for i in intersection:
#    print(i)
    if i[:3] == "KRW":
        KRWs.append(i)
    elif i[:3] == "BTC":
        BTCs.append(i)
    else:
        assert("Failed")

print("KRW market list : {}".format(KRWs))
print(len(KRWs))
print("BTC market list : {}".format(BTCs))
print(len(BTCs))
