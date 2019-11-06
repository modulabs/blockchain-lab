import requests
import json

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

def intersections(gopax_url, upbit_url):
    gopax_markets_list = markets(gopax_url)
    upbit_markets_list = markets(upbit_url)

    intersection = list(set(gopax_markets_list) & set(upbit_markets_list))

    KRWs = []
    BTCs = []

    for i in intersection:
        if i[:3] == "KRW":
            KRWs.append(i)
        elif i[:3] == "BTC":
            BTCs.append(i)
        else:
            assert("Failed")

    return KRWs, BTCs

if __name__ == "__main__":
    gopax_url = "https://api.gopax.co.kr/trading-pairs"
    upbit_url = "https://api.upbit.com/v1/market/all"

    KRWs, _ = intersections(gopax_url, upbit_url)

    print(KRWs)
