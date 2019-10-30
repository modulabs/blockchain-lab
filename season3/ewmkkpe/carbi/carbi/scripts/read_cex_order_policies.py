# -*- coding: utf-8 -*-
from gevent import monkey
monkey.patch_all()

import requests
import json
import math


url = 'https://cex.io/api/currency_limits'

r = requests.get(url)
assert r.status_code == 200

response = json.loads(r.text)
assert response['e'] == 'currency_limits'
assert response['ok'] == 'ok'
assert 'data' in response
assert 'pairs' in response['data']

order_policies = {}
for pair in response['data']['pairs']:
  quote_currency = pair['symbol1']
  base_currency = pair['symbol2']
  equity_pair = '{}/{}'.format(quote_currency.lower(), base_currency.lower())

  min_price = pair['minPrice']
  max_price = pair['maxPrice']

  # TODO(andrew): minLogSizeS2를 반영해야 함. 당장은 필요 없을 것으로 보임
  min_volume = pair['minLotSize']
  max_volume = pair['maxLotSize']

  print equity_pair, min_volume, max_volume, min_price, max_price

  order_policy = {}
  order_policy['price'] = {}

  if min_price is not None:
    order_policy['price']['min'] = float(min_price)
  if max_price is not None:
    order_policy['price']['max'] = float(max_price)

  order_policy['volume'] = {}

  if min_volume is not None:
    order_policy['volume']['min'] = float(min_volume)
  if max_volume is not None:
    order_policy['volume']['max'] = float(max_volume)

  order_policies[equity_pair] = order_policy

price_precisions = {}
price_precisions['btc/usd'] = 0.1
price_precisions['eth/usd'] = 0.01
price_precisions['bch/usd'] = 0.01
price_precisions['dash/usd'] = 0.01
price_precisions['zec/usd'] = 0.01
price_precisions['btg/usd'] = 0.01
price_precisions['xrp/usd'] = 0.0001
price_precisions['xlm/usd'] = 0.0001

price_precisions['btc/eur'] = 0.1
price_precisions['eth/eur'] = 0.01
price_precisions['bch/eur'] = 0.01
price_precisions['dash/eur'] = 0.01
price_precisions['zec/eur'] = 0.01
price_precisions['btg/eur'] = 0.01
price_precisions['xrp/eur'] = 0.0001
price_precisions['xlm/eur'] = 0.0001

price_precisions['btc/gbp'] = 0.1
price_precisions['eth/gbp'] = 0.01
price_precisions['bch/gbp'] = 0.01
price_precisions['dash/gbp'] = 0.01
price_precisions['zec/gbp'] = 0.01

price_precisions['ghs/btc'] = 0.00000001
price_precisions['eth/btc'] = 0.000001
price_precisions['bch/btc'] = 0.000001
price_precisions['dash/btc'] = 0.000001
price_precisions['zec/btc'] = 0.000001
price_precisions['btg/btc'] = 0.000001
price_precisions['xrp/btc'] = 0.00000001
price_precisions['xlm/btc'] = 0.00000001

price_precisions['btc/rub'] = 1

for equity_pair in order_policies:
  assert equity_pair in price_precisions, '{} not in price_precision'.format(equity_pair)
  step_size = price_precisions[equity_pair]
  order_policies[equity_pair]['price']['step'] = step_size

volume_digits = {}
volume_digits['btc'] = 8
volume_digits['eth'] = 8
volume_digits['bch'] = 8
volume_digits['xrp'] = 6
volume_digits['btg'] = 8
volume_digits['dash'] = 8
volume_digits['xlm'] = 7
volume_digits['zec'] = 8
volume_digits['ghs'] = 8


for equity_pair in order_policies:
  quote_currency = equity_pair.split("/")[0]
  assert quote_currency in volume_digits

  step_size = math.pow(10, 0 - volume_digits[quote_currency])
  order_policies[equity_pair]['volume']['step'] = step_size

print json.dumps(order_policies, indent=2)
