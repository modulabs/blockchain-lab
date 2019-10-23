# -*- coding: utf-8 -*-
import gevent
from gevent import monkey

monkey.patch_all()

import json
from carbi.client.exchange.http.coinone import CoinoneConfiguration, CoinoneClient
from carbi.client.exchange.http.bitfinex import BitfinexConfiguration, BitfinexClient
from carbi.client.exchange.http.okex import OkexConfiguration, OkexClient

coinone = None
bitfinex = None
okex = None

last_currency_updated_ts = 0
prev_currency_rate = None


def check_balance(coinone_currencies, bitfinex_currencies, transfering_quantities, transfering_currency):
  currency_balances = {}
  currency_balances['usdt'] = 0
  currencies = coinone_currencies + bitfinex_currencies + ['usdt']

  for currency in currencies:
    currency_balances[currency] = 0

  while True:
    r = coinone.get_balance()
    if 'krw' not in r:
      gevent.sleep(1)
      continue
    else:
      break
  currency_balances['krw'] = float(r['krw']['avail'])

  for currency in coinone_currencies:
    currency_balances[currency] += float(r[currency]['avail'])

  okex_future_balances = okex.get_future_balance()['info']
  for currency in okex_future_balances:
    if currency in currencies:
      currency_balances[currency] += float(okex_future_balances[currency]['account_rights'])

  okex_spot_balances = okex.get_spot_balance()['info']['funds']['free']
  for currency in okex_spot_balances:
    if currency in currencies:
      currency_balances[currency] += float(okex_spot_balances[currency])

  bitfinex_transfering_gimp_ratio = coinone.get_orderbook('{}/krw'.format(transfering_currency)).bid0_price \
                                    / bitfinex.get_orderbook('{}/usd'.format(transfering_currency)).ask0_price

  def estimate_asset_value(currency, quantity, transfering_quantity):
    if currency in coinone_currencies:
      orderbook = coinone.get_orderbook('{}/krw'.format(currency))
      price = orderbook.bid0_price
      return price * (quantity + transfering_quantity)
    elif currency in bitfinex_currencies:
      orderbook = bitfinex.get_orderbook('{}/usd'.format(currency))
      price = orderbook.bid0_price
      return price * (quantity + transfering_quantity) * bitfinex_transfering_gimp_ratio
    elif currency == 'usdt':
      return (quantity + transfering_quantity) * bitfinex_transfering_gimp_ratio

  print "==================== Currencies ===================="
  print 'KRW volume : {}'.format(currency_balances['krw'])
  for currency in currencies:
    print '{} volume : {}'.format(currency.upper(), currency_balances[currency])

  total_krw_value = 0
  for currency in currencies:
    value = estimate_asset_value(currency, currency_balances[currency], transfering_quantities[currency])
    total_krw_value += value

  bitfinex_margin_info = bitfinex.get_margin_information()

  bitfinex_required_margin = float(bitfinex_margin_info[0]['required_margin']) if 'required_margin' in bitfinex_margin_info[0] else 0
  bitfinex_net_value = float(bitfinex_margin_info[0]['net_value'])

  print "==================== Bitfinex ===================="
  if bitfinex_required_margin > 0:
    print 'bitfinex short required margin : {}'.format(bitfinex_required_margin)
  print 'bitfinex_transfering_gimp_ratio : {}'.format(bitfinex_transfering_gimp_ratio)
  print 'bitfinex net value : {}'.format(bitfinex_net_value)
  print "=================================================="

  print 'Total Position Value by KRW : ', bitfinex_net_value * bitfinex_transfering_gimp_ratio \
                                          + total_krw_value + transfering_quantities.get('krw', 0)


def main():
  global coinone
  conf_file = "conf/credentials/coinone.json"
  conf = CoinoneConfiguration.load_from_file(conf_file)
  coinone = CoinoneClient(conf)

  global bitfinex
  bitfinex_conf_file = "conf/credentials/bitfinex.json"
  bitfinex_conf = BitfinexConfiguration.load_from_file(bitfinex_conf_file)
  bitfinex = BitfinexClient(bitfinex_conf)

  global okex
  okex_conf_file = 'conf/credentials/okex.json'
  okex_conf = OkexConfiguration.load_from_file(okex_conf_file)
  okex = OkexClient(okex_conf)

  # API를 날리는 시간을 절약하기 위해서, 어떤 암호화폐 쌍을 들고 있는 지를 나열하면 해당 암호화폐에 대해서만 Query를 날립니다.
  coinone_currencies = ['eth', 'xrp', 'btc', 'bch', 'ltc', 'etc']
  bitfinex_currencies = ['eos', 'btg']

  # 현재 전송중이거나 다른 용도로 사용중이어서 거래소의 balance에 안 잡히는 암호화폐의 양이 얼마인지를 나타냅니다.
  transfering_quantities = {
    'btc': 0,
    'eth': 0,
    'xrp': 0,
    'bch': 0,
    'eos': 0,
    'etc': 0,
    'ltc': 0,
    'btg': 0,
    'krw': 0,
    'usd': 0,
    'usdt': 0,
  }

  # 어떤 암호화폐를 통해서 bitfinex에서 돈을 가지고 한국으로 가져올 것인지 정해야 합니다.
  transfering_currency = 'btc'

  # 다음과 같은 규칙으로 전체 포지션의 가치를 측정합니다.
  # 1. 일단 모든 한국으로 암호화폐를 전송해서 매도합니다. (최우선 매수호가에)
  # 2. 1.이 불가능한 모든 암호화폐를 bitfinex에서 청산합니다.
  # 3. bitfinex 에 남은 USD를 transfering_currency를 사서 한국으로 보내서 매도합니다.
  check_balance(coinone_currencies, bitfinex_currencies, transfering_quantities, transfering_currency)


def prettify(j):
  return json.dumps(j, indent=4)


# boiler plate
if __name__ == '__main__':
  main()
