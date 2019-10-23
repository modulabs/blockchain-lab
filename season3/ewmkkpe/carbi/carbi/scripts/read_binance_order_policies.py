# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()

import json
from carbi.client.exchange.http.binance import BinanceClient, BinanceConfiguration
import os


path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
config_path = os.path.join(path, 'conf/credentials/binance.json')

conf = BinanceConfiguration.load_from_file(config_path)
client = BinanceClient(conf)

response = client.get_exchange_info()

assert 'symbols' in response

rules = {}
for symbol in response['symbols']:
  # 내가 뭔가 잘못 알고 있는건가???
  base_currency = symbol['quoteAsset']
  quote_currency = symbol['baseAsset']

  # bch alias
  if base_currency.lower() == 'bcc':
    base_currency = 'bch'
  if quote_currency.lower() == 'bcc':
    quote_currency = 'bch'

  equity_pair = '{}/{}'.format(quote_currency.lower(), base_currency.lower())

  rule = {}
  filters = symbol['filters']

  for filter in filters:
    filter_type = filter['filterType']
    if filter_type == 'PRICE_FILTER':
      rule['price'] = {}
      if 'tickSize' in filter:
        rule['price']['step'] = float(filter['tickSize'])
      if 'minPrice' in filter:
        rule['price']['min'] = float(filter['minPrice'])
      if 'maxPrice' in filter:
        rule['price']['max'] = float(filter['maxPrice'])

    elif filter_type == 'LOT_SIZE':
      rule['volume'] = {}
      if 'stepSize' in filter:
        rule['volume']['step'] = float(filter['stepSize'])
      if 'minQty' in filter:
        rule['volume']['min'] = float(filter['minQty'])
      if 'maxQty' in filter:
        rule['volume']['max'] = float(filter['maxQty'])

    elif filter_type == 'MIN_NOTIONAL':
      rule['notional'] = {}
      if 'minNotional' in filter:
        rule['notional']['min'] = float(filter['minNotional'])

  rules[equity_pair] = rule


print json.dumps(rules, indent=2)
