# -*- coding: utf-8 -*-
import hashlib
import hmac
import json

import requests
import urllib

from carbi.client.exchange.pairs import ExchangeEquityPairs
from carbi.client.exchange.utils import public, private, validate_response
from carbi.struct.orderbook import Orderbook
from carbi.utils import ts

VALID_ORDERBOOK_LIMIT = [5, 10, 20, 50, 100, 500, 1000]

EQUITY_PAIRS = ExchangeEquityPairs('binance', pairs={
  'BTCUSDT': 'btc/usdt',
  'ETHUSDT': 'eth/usdt',
  'BCCUSDT': 'bch/usdt',
  'ETHBTC': 'eth/btc',
  'BCCBTC': 'bch/btc',
  'XRPBTC': 'xrp/btc',
  'BCCETH': 'bch/eth',
  'XRPETH': 'xrp/eth',
  'BNBBTC': 'bnb/btc',
  'BNBETH': 'bnb/eth',
  'BNBUSDT': 'bnb/usdt',
})


class BinanceConfiguration(object):
  __slots__ = (
    'key',
    'secret',
  )

  def __repr__(self):
    return json.dumps(self.__dict__, indent=2)

  @staticmethod
  def load_from_file(config_file):
    with open(config_file, "r") as f:
      content = json.load(f)
      config = BinanceConfiguration()
      config.key = content['key']
      config.secret = content['secret']
      return config


class BinanceClient(object):
  def __init__(self, conf):
    self.conf = conf

  @public
  def get_orderbook(self, equity_pair, depth=20):
    """
    거래소의 Orderbook을 조회한다.
    :param equity_pair: eth/btc 와 같은 형태의 equity pair 문자열
    :param depth: 조회할 Orderbook의 depth
    :return: Orderbook 객체
    """
    if depth <= 0:
      raise ValueError('Depth should be bigger than 0 : {}'.format(depth))
    if depth not in VALID_ORDERBOOK_LIMIT:
      raise ValueError('Depth should be one of {}'.format(VALID_ORDERBOOK_LIMIT))
    binance_equity_pair = EQUITY_PAIRS.to_exchange_pair(equity_pair)
    url = self._build_url('/api/v1/depth')
    params = dict(
      symbol=binance_equity_pair,
      limit=depth,
    )
    r = requests.get(url, params=params, timeout=5)
    response = json.loads(r.content)
    return BinanceParser.parse_orderbook_response(response, binance_equity_pair)

  @public
  def get_exchange_info(self):
    url = self._build_url('/api/v1/exchangeInfo')
    r = requests.get(url, timeout=5)
    response = json.loads(r.content)
    return response

  @private
  def _get(self, path, params={}, headers={}):
    headers['X-MBX-APIKEY'] = self.conf.key
    params['timestamp'] = ts()

    query_string = urllib.urlencode(params)
    signature = hmac.new(str(self.conf.secret), msg=str(query_string), digestmod=hashlib.sha256).hexdigest().upper()
    query_string += '&signature={}'.format(signature)

    url = self._build_url(path)
    url += "?{}".format(query_string)

    r = requests.get(url, headers=headers, timeout=5)
    # verify response first
    return json.loads(r.text)

  @private
  def _post(self, path, data={}, headers={}):
    headers['X-MBX-APIKEY'] = self.conf.key
    data['timestamp'] = ts()

    query_string = urllib.urlencode(data)
    signature = hmac.new(str(self.conf.secret), msg=str(query_string), digestmod=hashlib.sha256).hexdigest().upper()
    query_string += '&signature={}'.format(signature)

    url = self._build_url(path)

    r = requests.post(url, data=query_string, headers=headers, timeout=5)
    # verify response first
    return json.loads(r.text)

  @private
  def get_account_info(self):
    path = '/api/v3/account'
    return self._get(path)

  @private
  def get_balance(self):
    """
    :return: change form of response of get_account_info() to dict{ "coin": { "locked": double, "free": double }, ... }
    """
    r = self.get_account_info()
    result = {}
    for elem in r['balances']:
      result[elem['asset'].lower()] = {
        'locked': float(elem['locked']),
        'free': float(elem['free']),
      }

    return result

  @private
  def test_new_order(self, equity_pair, side, price, volume):
    path = "/api/v3/order/test"

    binance_equity_pair = EQUITY_PAIRS.to_exchange_pair(equity_pair)
    params = {
      'symbol': binance_equity_pair,
      'side': side,
      'type': 'MARKET',
      'quantity': volume,
    }

    return self._post(path, params)

  @private
  def market_buy(self, equity_pair, volume):
    path = '/api/v3/order'

    binance_equity_pair = EQUITY_PAIRS.to_exchange_pair(equity_pair)
    params = {
      'symbol': binance_equity_pair,
      'side': 'BUY',
      'type': 'MARKET',
      'quantity': volume,
    }

    return self._post(path, params)

  @private
  def market_sell(self, equity_pair, volume):
    path = '/api/v3/order'

    binance_equity_pair = EQUITY_PAIRS.to_exchange_pair(equity_pair)
    params = {
      'symbol': binance_equity_pair,
      'side': 'SELL',
      'type': 'MARKET',
      'quantity': volume,
    }

    return self._post(path, params)

  @private
  def withdraw(self, asset, volume, address, address_tag=None, name=None):
    """
    :param asset: btc, eth, ...
    :param volume: decimal value to withdraw
    :param address: target coin address
    :param address_tag: target coin address tag (optional for XMR, XRP)
    :param name: description of this address, optional
    :return:
    """
    path = '/wapi/v3/withdraw.html'

    params = {
      'asset': asset,
      'amount': volume,
      'address': address,
    }
    if address_tag is not None:
      params['addressTag'] = address_tag

    if name is not None:
      params['name'] = name

    return self._post(path, params)

  def _build_url(self, path):
    return 'https://api.binance.com' + path


class BinanceParser(Orderbook):
  @classmethod
  def parse_orderbook_response(cls, response, binance_equity_pair):
    validate_response(response, required_keys=['asks', 'bids', 'lastUpdateId'])
    assert len(response['asks']) != 0, 'INVALID_VALUE: orderbook:asks should not be empty'
    assert len(response['bids']) != 0, 'INVALID_VALUE: orderbook:bids should not be empty'
    equity_pair = EQUITY_PAIRS.from_exchange_pair(binance_equity_pair)
    asks = map(lambda elem: {'price': float(elem[0]), 'volume': float(elem[1])}, response['asks'])
    bids = map(lambda elem: {'price': float(elem[0]), 'volume': float(elem[1])}, response['bids'])
    timestamp = ts()
    return Orderbook('binance', equity_pair, asks, bids, timestamp)


class BinanceException(Exception):
  pass
