# -*- coding: utf-8 -*-
import hashlib
import hmac
import json

import requests

from carbi.client.exchange.nonce import NonceIssuer
from carbi.client.exchange.pairs import ExchangeEquityPairs
from carbi.client.exchange.utils import public, private, validate_response
from carbi.struct.orderbook import Orderbook

EQUITY_PAIRS = ExchangeEquityPairs('cex', pairs={
  'BTC:USD': 'btc/usd',
  'ETH:USD': 'eth/usd',
  'BCH:USD': 'bch/usd',
  'BTG:USD': 'btg/usd',
  'DASH:USD': 'dash/usd',
  'XRP:USD': 'xrp/usd',
  'ZEC:USD': 'zec/usd',
  'BTC:EUR': 'btc/eur',
  'ETH:EUR': 'eth/eur',
  'BCH:EUR': 'bch/eur',
  'BTG:EUR': 'btg/eur',
  'DASH:EUR': 'dash/eur',
  'XRP:EUR': 'xrp/eur',
  'ZEC:EUR': 'zec/eur',
  'BTC:RUB': 'btc/rub',
  'ETH:BTC': 'eth/btc',
  'BCH:BTC': 'bch/btc',
  'BTG:BTC': 'btg/btc',
  'DASH:BTC': 'dash/btc',
  'XRP:BTC': 'xrp/btc',
  'ZEC:BTC': 'zec/btc',
  'GHS:BTC': 'ghs/btc',
})


class CexConfiguration(object):
  __slots__ = (
    'user_id',
    'key',
    'secret',
  )

  def __repr__(self):
    return json.dumps(self.__dict__, indent=2)

  @staticmethod
  def load_from_file(config_file):
    with open(config_file, "r") as f:
      content = json.load(f)
      config = CexConfiguration()
      config.user_id = content['user_id']
      config.key = content['key']
      config.secret = content['secret']
      return config


class CexClient(object):
  def __init__(self, conf):
    self.conf = conf
    self.nonce_issuer = NonceIssuer()

  def _get_signature(self, nonce):
    message = str(nonce) + self.conf.user_id + self.conf.key
    signature = hmac.new(str(self.conf.secret), msg=str(message), digestmod=hashlib.sha256).hexdigest().upper()
    return signature

  def _get_basic_private_data(self):
    nonce = self.nonce_issuer.next_nonce()
    signature = self._get_signature(nonce)
    return {
      'nonce': nonce,
      'signature': signature,
      'key': self.conf.key,
    }

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
    target_equity, base_equity = equity_pair.split("/")
    url = "https://cex.io/api/order_book/{}/{}/".format(target_equity.upper(), base_equity.upper())
    params = dict(
      depth=depth,
    )
    r = requests.get(url, params=params, timeout=5)
    response = json.loads(r.content)
    return CexParser.parse_orderbook_response(response)

  @private
  def get_balance(self):
    """
    private API
    {
      "timestamp": "1509886058",
      "BTC": {
          "available": "0.48696717",
          "orders": "0.00000000"
      },
      "ETH": {
          "available": "9.82155000",
          "orders": "0.10000000"
      },
      ...
    }
    현재 limit에 걸린 물량은 orders에 올라가고, 아닌 물량은 available에 보이는 듯
    :return:
    """
    url = "https://cex.io/api/balance/"
    data = self._get_basic_private_data()

    r = requests.post(url, data=data)
    return json.loads(r.content)

  @private
  def get_myfee(self):
    url = "https://cex.io/api/get_myfee/"
    data = self._get_basic_private_data()

    r = requests.post(url, data=data)
    j = json.loads(r.content)
    CexResponseHandler.raise_if_exception(j)
    return j

  @private
  def place_buy_order(self, amount, price, currency='btc'):
    """
    Only for BTC/USD now, can be fixed with changed url
    :return:
      complete: Boolean
      price: String float
      amount: String float
      time: long
      type: String
      id: String long
      pending: String float
    """
    url = "https://cex.io/api/place_order/{}/USD".format(currency.upper())
    data = self._get_basic_private_data()

    data['type'] = 'buy'
    data['amount'] = amount
    data['price'] = price

    r = requests.post(url, data=data)
    j = json.loads(r.content)
    CexResponseHandler.raise_if_exception(j)
    return j

  @private
  def place_sell_order(self, amount, price, currency='btc'):
    url = "https://cex.io/api/place_order/{}/USD".format(currency.upper())
    data = self._get_basic_private_data()

    data['type'] = 'sell'
    data['amount'] = amount
    data['price'] = price

    r = requests.post(url, data=data)
    j = json.loads(r.content)
    CexResponseHandler.raise_if_exception(j)
    return j

  @private
  def cancel_order(self, id):
    url = "https://cex.io/api/cancel_order/"
    data = self._get_basic_private_data()

    data['id'] = id
    r = requests.post(url, data=data)
    if r.content == "true":
      return r.content
    else:
      raise CexException("Cancel Order [{}] is failed.".format(id))

  @private
  def get_active_orders(self):
    """
    일단 BTC/USD 만을 기준으로 합니다.
    :return: list of
      id: String
      time: String, Long
      type: String (buy/sell)
      price: String, float
      amount: String, float
      pending: String, float
      symbol1: String
      symbol2: String
    """
    url = "https://cex.io/api/open_orders/BTC/USD"
    data = self._get_basic_private_data()

    r = requests.post(url, data=data)
    return json.loads(r.content)

  @private
  def get_active_orders_with_id(self, ids):
    """
    e: String
    ok: String
    data : List of List
      inside list : [order_id, total_volume, pending_volume]
    :param ids:
    :return:
    """
    if len(ids) == 0:
      raise CexException("Number of id should be bigger than 0")

    url = "https://cex.io/api/active_orders_status"
    data = self._get_basic_private_data()

    data['orders_list'] = ids
    r = requests.post(url, data=data)
    j = json.loads(r.content)
    CexResponseHandler.raise_if_exception(j)
    return j

  @private
  def get_open_positions(self, currency):
    """
    :param currency: String, 'btc', 'eth', 'bch'
    :return:
    """
    url = "https://cex.io/api/open_positions/{}/USD".format(currency.upper())
    data = self._get_basic_private_data()

    r = requests.post(url, data=data)
    j = json.loads(r.content)
    CexResponseHandler.raise_if_exception(j)
    return j


class CexResponseHandler(object):
  @staticmethod
  def raise_if_exception(response):
    if 'error' in response:
      error_message = response['error']
      if error_message == 'Nonce must be incremented':
        raise CexNonceException(error_message)
      raise CexException(error_message)


class CexParser(Orderbook):
  @classmethod
  def parse_orderbook_response(cls, response):
    validate_response(response, required_keys=['asks', 'bids', 'pair', 'timestamp'])
    assert len(response['asks']) != 0, 'INVALID_VALUE: orderbook:asks should not be empty'
    assert len(response['bids']) != 0, 'INVALID_VALUE: orderbook:bids should not be empty'
    equity_pair = EQUITY_PAIRS.from_exchange_pair(response['pair'])
    asks = map(lambda elem: {'price': elem[0], 'volume': elem[1]}, response['asks'])
    bids = map(lambda elem: {'price': elem[0], 'volume': elem[1]}, response['bids'])
    timestamp = int(response['timestamp']) * 1000
    return Orderbook('cex', equity_pair, asks, bids, timestamp)


class CexException(Exception):
  pass


class CexNonceException(CexException):
  pass
