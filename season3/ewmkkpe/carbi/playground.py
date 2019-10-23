#-*- coding: utf-8 -*-
import gevent
from gevent import monkey

monkey.patch_all()

import json
from carbi.client.exchange.http.coinone import CoinoneConfiguration, CoinoneClient
from carbi.client.exchange.http.poloniex import PoloniexConfiguration, PoloniexClient
from carbi.client.exchange.http.cex import CexConfiguration, CexClient
from carbi.client.exchange.http.bitfinex import BitfinexConfiguration, BitfinexClient
from carbi.client.exchange.http.binance import BinanceClient, BinanceConfiguration
from carbi.client.exchange.websocket.binance import BinanceWebSocketClient
from carbi.client.exchange.http.okex import OkexClient, OkexConfiguration
from carbi.client.exchange.http.korbit import KorbitClient
import time
import urllib2
import requests
import sys
from carbi.utils.gevent_utils import gevent_map, gevent_call_async

coinone = None
poloniex = None
cex = None
korbit = None
last_currency_updated_ts = 0
prev_currency_rate = None


def main():
  global coinone
  conf_file = "conf/credentials/coinone.json"
  conf = CoinoneConfiguration.load_from_file(conf_file)
  coinone = CoinoneClient(conf)

  global poloniex
  conf_file = "conf/credentials/poloniex.json"
  conf = PoloniexConfiguration.load_from_file(conf_file)
  poloniex = PoloniexClient(conf)

  global cex
  conf_file = "conf/credentials/cex.json"
  conf = CexConfiguration.load_from_file(conf_file)
  cex = CexClient(conf)

  conf_file = 'conf/credentials/bitfinex.json'
  conf = BitfinexConfiguration.load_from_file(conf_file)
  bitfinex = BitfinexClient(conf)

  korbit = KorbitClient()

  # binance = BinanceWebSocketClient(config=None)

  conf_file = 'conf/credentials/binance.json'
  conf = BinanceConfiguration.load_from_file(conf_file)
  binance = BinanceClient(conf)

  conf_file = 'conf/credentials/okex.json'
  conf = OkexConfiguration.load_from_file(conf_file)
  okex = OkexClient(conf)


  from datetime import datetime
  from datetime import timedelta
  import pytz

  dt = datetime.now(pytz.UTC)
  dt.replace

  # 0이 월요일, 1이 화요일 -> 이번주 안에
  # 4가 금요일 -> 한국시간 오후 5시, 중국시간 오후 4시 (UTC+0800) 에 delivery,
  # 5가 토요일 -> 다음주로
  # 6이 일요일
  print dt.weekday()
  print (dt + timedelta(days=1)).weekday()
  print (dt + timedelta(days=2)).weekday()

  def find_delivery_dt_of_the_week(dt):
    from datetime import timedelta
    dt = dt + timedelta(days=(4 - dt.weekday()))
    return dt.replace(hour=8, minute=0, second=0, microsecond=0)

  def find_delivery_dt_of_the_quarter(dt):
    from datetime import timedelta
    # 1. move to 3, 6, 9, 12 month
    # 2. move to upcoming friday
    # 3.
    pass

  # print find_delivery_dt_of_the_week(dt=datetime.now(pytz.UTC))
  print find_delivery_dt_of_the_week(dt=datetime.now(pytz.UTC))

  print datetime.now(pytz.UTC)+timedelta(days=-10)
  print find_delivery_dt_of_the_week(dt=datetime.now(pytz.UTC)+timedelta(days=-10))

  for order in okex.get_future_order_info('ltc/usd', 'quarter'):
    print order['symbol'], order['price_avg'], order['unit_amount'] * order['amount'] / order['price_avg'], order['fee']

  return

  iteration_count = 0
  max_iteration_count = 10

  # print prettify(okex.get_future_positions('eos/usd', 'this_week'))
  # print prettify(okex.get_future_positions('eos/usd', 'next_week'))
  # print prettify(okex.get_future_positions('eos/usd', 'quarter'))
  # return

  while True:
    # equity_pairs = ['eos/usd', 'etc/usd', 'eth/usd', 'btc/usd', 'bch/usd', 'xrp/usd', 'ltc/usd']
    equity_pairs = ['eos/usd', 'btc/usd', 'bch/usd']
    for equity_pair in equity_pairs:
      # equity_pair = 'eos/usd'
      contract_type = 'this_week'

      def get_orderbook(contract_type):
        return okex.get_future_orderbook(equity_pair, contract_type)

      try:
        r = gevent_map(get_orderbook, ['this_week', 'next_week', 'quarter'])

        this_week = r[0]
        next_week = r[1]
        quarter = r[2]

        contract_size = 10

        # this_week long -> next_week long rollover
        # this week short, next week long
        print '{0} rollover     : {1:.3f} % : {2:.0f} USD'.format(
          equity_pair, this_week.bid0_price / next_week.ask0_price * 100 - 100, contract_size * min(this_week.bid0_volume, next_week.ask0_volume))

        print '{0} rollover add : {1:.3f} % : {2:.0f} USD'.format(
          equity_pair, next_week.bid0_price / this_week.ask0_price * 100 - 100,
                       contract_size * min(this_week.bid0_volume, next_week.ask0_volume))

        # add position (next week long, quarter short)
        print '{0} new position : {1:.3f} % : {2:.0f} USD'.format(
          equity_pair, quarter.bid0_price / next_week.ask0_price * 100 - 100, contract_size * min(quarter.bid0_volume, next_week.ask0_volume))

        print '{0} position close : {1:.3f} % : {2:.0f} USD'.format(
          equity_pair, next_week.bid0_price / quarter.ask0_price * 100 - 100, contract_size * min(quarter.ask0_volume, next_week.bid0_volume))

        if this_week.bid0_price / next_week.ask0_price > 1.001:
          # rollover
          volume = min(this_week.bid0_volume, next_week.ask0_volume)

          print 'Try to rollover position {}, {} USD'.format(equity_pair, volume * 10)
          sell_price = this_week.bid0_price * 0.99
          buy_price = next_week.ask0_price * 1.01
          # print okex.place_future_buy(equity_pair, 'next_week', price=buy_price, volume=volume, open_position=True)
          # print okex.place_future_sell(equity_pair, 'this_week', price=sell_price, volume=volume, open_position=False)

        if quarter.bid0_price / next_week.ask0_price > 1.035:
          # add new position
          # max position add per iteration should be smaller than 500 USD
          volume = min(quarter.bid0_volume, next_week.ask0_volume, 100)

          print 'Try to add position {}, {} USD'.format(equity_pair, volume * 10)
          sell_price = quarter.bid0_price * 0.99
          buy_price = next_week.ask0_price * 1.01

          # buy_result = gevent_call_async(okex.place_future_buy, equity_pair, 'next_week', price=buy_price, volume=volume, open_position=True)
          # sell_result = gevent_call_async(okex.place_future_sell, equity_pair, 'quarter', price=sell_price, volume=volume, open_position=True)
          # print buy_result.get()
          # print sell_result.get()
      except Exception as e:
        print 'Exception', e
        print sys.exc_info()

      gevent.sleep(2)
      # iteration_count += 1
      print '============================================================='

  return


def prettify(j):
  return json.dumps(j, indent=4)


# boiler plate
if __name__ == '__main__':
    main()
