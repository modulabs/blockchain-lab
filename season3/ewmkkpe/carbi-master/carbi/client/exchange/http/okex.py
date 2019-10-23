# -*- coding: utf-8 -*-
import hashlib
import json

import requests

from carbi.client.exchange.nonce import NonceIssuer
from carbi.client.exchange.pairs import ExchangeEquityPairs
from carbi.client.exchange.utils import public, private, validate_response
from carbi.struct.orderbook import Orderbook
from carbi.utils import ts
from carbi.utils.dyprops import DynamicProperties
from carbi.utils.okex import check_valid_contract_type, get_future_expiry_symbol

EQUITY_PAIRS = ExchangeEquityPairs('okex', pairs={
  'btc_usd': 'btc/usd',
  'eth_usd': 'eth/usd',
  'bch_usd': 'bch/usd',
  'etc_usd': 'etc/usd',
  'eos_usd': 'eos/usd',
  'xrp_usd': 'xrp/usd',
  'ltc_usd': 'ltc/usd',
  'btg_usd': 'btg/usd',
  'btc_usdt': 'btc/usdt',
  'eth_usdt': 'eth/usdt',
  'bch_usdt': 'bch/usdt',
  'etc_usdt': 'etc/usdt',
  'eos_usdt': 'eos/usdt',
  'xrp_usdt': 'xrp/usdt',
  'ltc_usdt': 'ltc/usdt',
  'btg_usdt': 'btg/usdt',
})


class OkexConfiguration(DynamicProperties):
  @staticmethod
  def load_from_file(config_file):
    with open(config_file, "r") as f:
      content = json.load(f)
      config = OkexConfiguration()
      config.key = content['key']
      config.secret = content['secret']
      return config


class OkexConditions(object):
  @staticmethod
  def check_contract_type(contract_type):
    check_valid_contract_type(contract_type)

  @staticmethod
  def check_orderbook_depth(depth):
    assert 5 <= depth <= 200, 'INVALID DEPTH: [{}] (Invalid: between 5 and 200)'.format(depth)


class OkexAuthenticatedRequester(object):
  def __init__(self, config):
    self.config = config

  def post(self, url, params):
    data = self._get_signed_query_string(params)
    headers = {
      "Content-type": "application/x-www-form-urlencoded",
    }
    r = requests.post(url, data=data, headers=headers, timeout=5)
    response = json.loads(r.content)
    return response

  def _get_signed_query_string(self, params):
    query_strings = []
    for key in sorted(params.keys()):
      query_strings.append("{}={}".format(key, params[key]))
    query_string = '&'.join(query_strings)
    query_string_with_secret = query_string + '&secret_key={}'.format(self.config.secret)
    sign = hashlib.md5(query_string_with_secret.encode('utf8')).hexdigest().upper()
    return query_string + '&sign={}'.format(sign)


class OkexClient(object):
  def __init__(self, config):
    self.config = config
    self.nonce_issuer = NonceIssuer()
    self.authenticated_requester = OkexAuthenticatedRequester(config)

  @public
  def get_spot_orderbook(self, equity_pair, depth=20):
    OkexConditions.check_orderbook_depth(depth)

    okex_equity_pair = EQUITY_PAIRS.to_exchange_pair(equity_pair)
    url = 'https://www.okex.com/api/v1/depth.do'
    params = {
      'symbol': okex_equity_pair,
      'size': depth,
    }
    r = requests.get(url, params, timeout=1)
    response = json.loads(r.content)
    return OkexParser.parse_orderbook_response(response, okex_equity_pair)

  @public
  def get_future_orderbook(self, equity_pair, contract_type, depth=20):
    OkexConditions.check_contract_type(contract_type)
    OkexConditions.check_orderbook_depth(depth)

    okex_equity_pair = EQUITY_PAIRS.to_exchange_pair(equity_pair)
    url = 'https://www.okex.com/api/v1/future_depth.do'
    params = {
      'symbol': okex_equity_pair,
      'contract_type': contract_type,
      'size': depth,
    }
    r = requests.get(url, params, timeout=1)
    response = json.loads(r.content)
    return OkexParser.parse_orderbook_response(response, okex_equity_pair, contract_type=contract_type)

  @private
  def get_future_balance(self):
    url = 'https://www.okex.com/api/v1/future_userinfo.do'
    params = {
      'api_key': self.config.key
    }
    return self.authenticated_requester.post(url, params)

  @private
  def get_spot_balance(self):
    url = 'https://www.okex.com/api/v1/userinfo.do'
    params = {
      'api_key': self.config.key
    }
    return self.authenticated_requester.post(url, params)

  @private
  def get_future_order_info(self, equity_pair, contract_type):
    """
    History of filled/not filled private future order
    :return:
    """
    check_valid_contract_type(contract_type)

    url = 'https://www.okex.com/api/v1/future_order_info.do'

    current_page = 1
    orders = []

    while True:
      params = {
        'api_key': self.config.key,
        'symbol': EQUITY_PAIRS.to_exchange_pair(equity_pair),
        'contract_type': contract_type,
        'status': 2,  # filled
        'order_id': -1,  # filter on status
        'page_length': 50,
        'current_page': current_page,
      }
      response = self.authenticated_requester.post(url, params)

      assert response['result'], 'result is not true, something wrong, {}'.format(response)
      for order in response['orders']:
        orders.append(order)

      if len(response['orders']) < 50:
        return sorted(orders, key=lambda x: x['order_id'])
      else:
        current_page += 1

  @private
  def place_future_buy(self, equity_pair, contract_type, price, volume, lever_rate=20, open_position=True):
    OkexConditions.check_contract_type(contract_type)
    url = 'https://www.okex.com/api/v1/future_trade.do'
    params = {
      'symbol': EQUITY_PAIRS.to_exchange_pair(equity_pair),
      'contract_type': contract_type,
      'api_key': self.config.key,
      'price': price,
      'amount': volume,
      'type': 1 if open_position else 4,
      'match_price': 0,  # not BBO
      'lever_rate': lever_rate,
    }
    return self.authenticated_requester.post(url, params)

  @private
  def place_future_sell(self, equity_pair, contract_type, price, volume, lever_rate=20, open_position=True):
    OkexConditions.check_contract_type(contract_type)
    url = 'https://www.okex.com/api/v1/future_trade.do'
    params = {
      'symbol': EQUITY_PAIRS.to_exchange_pair(equity_pair),
      'contract_type': contract_type,
      'api_key': self.config.key,
      'price': price,
      'amount': volume,
      'type': 2 if open_position else 3,
      'match_price': 0,  # not BBO
      'lever_rate': lever_rate,
    }
    return self.authenticated_requester.post(url, params)

  @private
  def get_future_positions(self, equity_pair, contract_type):
    OkexConditions.check_contract_type(contract_type)
    url = 'https://www.okex.com/api/v1/future_position.do'
    params = {
      'symbol': EQUITY_PAIRS.to_exchange_pair(equity_pair),
      'contract_type': contract_type,
      'api_key': self.config.key,
    }
    return self.authenticated_requester.post(url, params)


class OkexParser(Orderbook):
  @classmethod
  def parse_orderbook_response(cls, response, okex_equity_pair, contract_type=None):
    validate_response(response, required_keys=['asks', 'bids'])
    assert len(response['asks']) != 0, 'INVALID_VALUE: orderbook:asks should not be empty'
    assert len(response['bids']) != 0, 'INVALID_VALUE: orderbook:bids should not be empty'
    equity_pair = EQUITY_PAIRS.from_exchange_pair(okex_equity_pair)

    # 만약 contract_type이 주어진 경우 선물에 대한 오더북이다.
    # 이 경우에는 equity_pair를 선물 포맷에 맞게 변형해서 넣어줘야 한다.
    if contract_type is not None:
      expiry_yymmdd = get_future_expiry_symbol(contract_type)
      equity_pair = 'f_{}_{}'.format(equity_pair, expiry_yymmdd)

    asks = sorted(response['asks'], key=lambda b: b[0])
    bids = sorted(response['bids'], key=lambda b: b[0], reverse=True)
    asks = map(lambda elem: {'price': elem[0], 'volume': elem[1]}, asks)
    bids = map(lambda elem: {'price': elem[0], 'volume': elem[1]}, bids)
    timestamp = ts()
    return Orderbook('okex', equity_pair, asks, bids, timestamp)


class OkexException(Exception):
  pass
