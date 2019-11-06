import requests
import json

from MARKETS import *

def upbit_orderbook(market):
    upbit_url = "https://api.upbit.com/v1/orderbook"
    querystring = {"markets":market}
    response = requests.request("GET", upbit_url, params=querystring)

    res = json.loads(response.text)
    return res

def upbit_bid_ask_list(uob, n):
    bids_n_asks = uob['orderbook_units']
    asks_price = []
    asks_size = []
    bids_price = []
    bids_size = []

    for bid_n_ask in bids_n_asks:
        asks_price.append(bid_n_ask['ask_price'])
        asks_size.append(bid_n_ask['ask_size'])
        bids_price.append(bid_n_ask['bid_price'])
        bids_size.append(bid_n_ask['bid_size'])

    return asks_price[:n], asks_size[:n], bids_price[:n], bids_size[:n]

def gopax_orderbook(market):
    gopax_url = "https://api.gopax.co.kr/trading-pairs/{}/book".format(market)
    response = requests.request("GET", gopax_url)

    res = json.loads(response.text)
    return res

def gopax_bid_ask_list(gob, n):
    bids = gob['bid']
    asks = gob['ask']

    asks_price = []
    asks_size = []
    bids_price = []
    bids_size = []

    for bid in bids[:n]:
        print(bid)

    for ask in asks[:n]:
        print(ask)

#    for bid_n_ask in bids_n_asks:
#        asks_price.append(bid_n_ask['ask_price'])
#        asks_size.append(bid_n_ask['ask_size'])
#        bids_price.append(bid_n_ask['bid_price'])
#        bids_size.append(bid_n_ask['bid_size'])

    return asks_price, asks_size, bids_price, bids_size

def market_name_swap(market):
    split = market.split("-")
    return "{}-{}".format(split[1], split[0])

if __name__ == "__main__":
#    gopax_market_url = "https://api.gopax.co.kr/trading-pairs"
#    upbit_market_url = "https://api.upbit.com/v1/market/all"

#    KRWs, _ = intersections(gopax_market_url, upbit_market_url)
#    KRWs = ['KRW-EOS', 'KRW-ENJ', 'KRW-LOOM', 'KRW-ZIL', 'KRW-SBD', 'KRW-MOC', 'KRW-STEEM', 'KRW-GNT', 'KRW-AERGO', 'KRW-XRP', 'KRW-ELF', 'KRW-BTC', 'KRW-ETH', 'KRW-KNC', 'KRW-OMG', 'KRW-SNT', 'KRW-BAT', 'KRW-XLM', 'KRW-QTUM', 'KRW-BCH', 'KRW-REP', 'KRW-ZRX', 'KRW-CVC', 'KRW-LTC', 'KRW-IOST', 'KRW-MCO']
    KRWs = ['KRW-EOS']

    for market in KRWs:
#        uob = upbit_orderbook(market)[0]
#        upbit_asks_price, upbit_asks_size, upbit_bids_price, upbit_bids_sizes = upbit_bid_ask_list(uob)
        gob = gopax_orderbook(market_name_swap(market))
        gopax_bid_ask_list(gob, 10)
