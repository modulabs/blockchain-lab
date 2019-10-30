# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import math

import requests

from carbi.client.exchange import constants
from carbi.client.exchange.nonce import NonceIssuer
from carbi.client.exchange.pairs import ExchangeEquityPairs
from carbi.client.exchange.utils import public, validate_response
from carbi.struct.orderbook import Orderbook

EQUITY_PAIRS = ExchangeEquityPairs('coinone', pairs={
  'btc': 'btc/krw',
  'bch': 'bch/krw',
  'eth': 'eth/krw',
  'etc': 'etc/krw',
  'xrp': 'xrp/krw',
  'qtum': 'qtum/krw',
  'iota': 'iota/krw',
  'ltc': 'ltc/krw',
  'btg': 'btg/krw',
})


class CoinoneConfiguration(object):
  __slots__ = (
    'access_token',
    'secret_key',
  )

  def __repr__(self):
    return json.dumps(self.__dict__, indent=2)

  @staticmethod
  def load_from_file(config_file):
    with open(config_file, "r") as f:
      content = json.load(f)
      config = CoinoneConfiguration()
      config.access_token = content['access_token']
      config.secret_key = content['secret_key']
      return config


class CoinoneClient(object):
  def __init__(self, conf):
    self.conf = conf
    self.nonce_issuer = NonceIssuer()

  @staticmethod
  def public_base_url():
    return 'https://api.coinone.co.kr/'

  @staticmethod
  def base_url():
    return 'https://api.coinone.co.kr/v2/'

  @staticmethod
  def base_url_v1():
    return 'https://api.coinone.co.kr/v1/'

  def get_encoded_payload(self, payload):
    payload[u'nonce'] = self.nonce_issuer.next_nonce()

    dumped_json = json.dumps(payload)
    encoded_json = base64.b64encode(dumped_json)
    return encoded_json

  def get_signature(self, encoded_payload):
    signature = hmac.new(str(self.conf.secret_key).upper(), str(encoded_payload), hashlib.sha512)
    return signature.hexdigest()

  def post(self, url, payload):
    encoded_payload = self.get_encoded_payload(payload)
    headers = {
      'Content-type': 'application/json',
      'User-Agent': constants.USER_AGENT,
      'X-COINONE-PAYLOAD': encoded_payload,
      'X-COINONE-SIGNATURE': self.get_signature(encoded_payload)
    }
    r = requests.post(url, headers=headers, data=encoded_payload, timeout=10)
    j = json.loads(r.content)
    if 'errorCode' in j:
      if j['errorCode'] != "0":
        if 'errorMsg' in j:
          error_message = j['errorMsg']
          raise CoinoneException(error_message)
        else:
          error_code = j['errorCode']
          if error_code == "131":
            raise CoinoneNonceException('Coinone Exception with nonce')

          raise CoinoneException('Coinone Exception with error code[{}]'.format(error_code))
    return j

  def get(self, url, params, timeout=5):
    ## public get 만 이 형태일 수도 있습니다.
    headers = {
      'Content-type': 'application/json',
      'User-Agent': constants.USER_AGENT,
    }
    r = requests.get(url, headers=headers, params=params, timeout=timeout)
    j = json.loads(r.content)
    if 'errorCode' in j:
      if j['errorCode'] != "0":
        if 'errorMsg' in j:
          error_message = j['errorMsg']
          raise CoinoneException(error_message)
        else:
          error_code = j['errorCode']
          if error_code == "131":
            raise CoinoneNonceException('Coinone Exception with nonce')

          raise CoinoneException('Coinone Exception with error code[{}]'.format(error_code))
    return j

  def get_balance(self):
    """
    계좌에 남은 KRW, BTC, ETH 등을 가져옵니다.
    """
    url = CoinoneClient.base_url() + "account/balance/"
    payload = {"access_token": self.conf.access_token}
    return self.post(url, payload)

  @public
  def get_orderbook(self, equity_pair):
    """
    거래소의 Orderbook을 조회한다.
    Korbit의 경우 파라메터에 depth가 없다.
    :param equity_pair: eth/btc 와 같은 형태의 equity pair 문자열
    :return: Orderbook 객체
    """
    currency = EQUITY_PAIRS.to_exchange_pair(equity_pair)
    url = 'http://api.coinone.co.kr/orderbook/'
    params = dict(
      currency=currency
    )
    response = self.get(url, params=params, timeout=5)
    return CoinoneParser.parse_orderbook_response(response)

  def buy_currency(self, currency, krw):
    """
    시장가로 currency를 krw만큼 사달라고 요청합니다. (qty가 아니라 krw임을 주의할 것)
    """
    url = CoinoneClient.base_url() + "order/market_buy/"
    payload = {
      "access_token": self.conf.access_token,
      "currency": currency,
      "price": krw,
    }
    return self.post(url, payload)

  def sell_currency(self, currency, qty):
    """
    시장가로 currency를 qty만큼 팔아달라고 요청합니다.
    """
    url = CoinoneClient.base_url() + "order/market_sell/"
    payload = {
      "access_token": self.conf.access_token,
      "currency": currency,
      "qty": qty,
    }
    return self.post(url, payload)

  def my_completed_orders(self, currency):
    """
    내 계정으로 특정 currency에 대해서 일어났던 거래를 전부 불러옵니다. pagination이 안되어 있어서 나중에 문제를 일으킬 수 있습니다.
    """
    url = CoinoneClient.base_url() + 'order/complete_orders/'
    payload = {
      "access_token": self.conf.access_token,
      "currency": currency,
    }
    return self.post(url, payload)

  def my_completed_orders_of_id(self, currency, order_id):
    """
    :param currency:
    :param order_id:
    :return: list of completed_order - {orderId, fee, timestamp, price, qty, feeRate, type}
    """
    # order_id 가 처음에 request를 보낼때는 소문자로 오는데 나중에 completed_order에서 가져올 때는 대문자로 옴...
    order_id = order_id.upper()

    url = CoinoneClient.base_url() + 'order/complete_orders/'
    payload = {
      "access_token": self.conf.access_token,
      "currency": currency,
    }
    response = self.post(url, payload)

    result = []
    if response['result'] == 'success':
      completed_orders = response['completeOrders']
      for completed_order in completed_orders:
        if completed_order['orderId'] == order_id:
          result.append(completed_order)
      return result
    else:
      raise Exception('result code is not success : ' + response)

  def buy_limit(self, currency, price, qty):
    """
    market limit 가격으로 특정 currency를 qty만큼 사달라고 요청합니다. BTC/KRW buy 거래입니다.
    :param currency:
    :param price:
    :param qty:
    :return:
    """
    if not self.check_price_format(currency, price):
      raise ValueError()

    url = CoinoneClient.base_url() + 'order/limit_buy/'
    payload = {
      "access_token": self.conf.access_token,
      'currency': currency,
      'price': int(price),
      'qty': qty,
    }
    return self.post(url, payload)

  def sell_limit(self, currency, price, qty):
    """
    market limit 가격으로 특정 currency를 qty만큼 팔아달라고 요청합니다. BTC/KRW sell 거래입니다.
    :param currency:
    :param price:
    :param qty:
    :return:
    """
    if not self.check_price_format(currency, price):
      raise ValueError()

    url = CoinoneClient.base_url() + 'order/limit_sell/'
    payload = {
      "access_token": self.conf.access_token,
      'currency': currency,
      'price': int(price),
      'qty': qty,
    }
    return self.post(url, payload)

  def check_price_format(self, currency, price):
    if currency.lower() == 'btc':
      return price % 1000 == 0
    elif currency.lower() == 'eth':
      return price % 100 == 0
    elif currency.lower() == 'bch':
      return price % 500 == 0
    elif currency.lower() == 'xrp':
      return price % 1 == 0
    else:
      raise NotImplementedError("Price unit of {} is not informed.".format(currency))

  def floor_price_format(self, currency, price):
    if currency.lower() == 'btc':
      return 1000 * math.floor(price / 1000.0)
    elif currency.lower() == 'eth':
      return 100 * math.floor(price / 100.0)
    elif currency.lower() == 'bch':
      return 500 * math.floor(price / 500.0)
    elif currency.lower() == 'xrp':
      return 1 * math.floor(price / 1)
    else:
      raise NotImplementedError("Price unit of {} is not informed.".format(currency))

  def ceil_price_format(self, currency, price):
    if currency.lower() == 'btc':
      return 1000 * math.ceil(price / 1000.0)
    elif currency.lower() == 'eth':
      return 100 * math.ceil(price / 100.0)
    elif currency.lower() == 'bch':
      return 500 * math.ceil(price / 500.0)
    elif currency.lower() == 'xrp':
      return 1 * math.ceil(price / 1)
    else:
      raise NotImplementedError("Price unit of {} is not informed.".format(currency))

  def get_2fa_number(self, type):
    """
    이거 뭐 폰으로 문자가 와? ㅋㅋㅋ 이러면 쓸 수가 없는데...
    :param type:
    :return:
    """
    url = CoinoneClient.base_url() + 'transaction/auth_number/'
    payload = {
      "access_token": self.conf.access_token,
      'type': type,
      'nonce': self.nonce_issuer.next_nonce()
    }
    return self.post(url, payload)

  def get_transaction_history(self, currency):
    url = CoinoneClient.base_url() + 'transaction/history/'
    payload = {
      "access_token": self.conf.access_token,
      'currency': currency,
      'nonce': self.nonce_issuer.next_nonce()
    }
    return self.post(url, payload)


class CoinoneParser(object):
  @classmethod
  def parse_orderbook_response(cls, response):
    validate_response(response, required_keys=['ask', 'bid', 'currency'])
    assert len(response['ask']) != 0, 'INVALID_VALUE: orderbook:asks should not be empty'
    assert len(response['bid']) != 0, 'INVALID_VALUE: orderbook:bids should not be empty'
    equity_pair = EQUITY_PAIRS.from_exchange_pair(response['currency'])
    asks = map(lambda elem: {'price': float(elem['price']), 'volume': float(elem['qty'])}, response['ask'])
    bids = map(lambda elem: {'price': float(elem['price']), 'volume': float(elem['qty'])}, response['bid'])
    timestamp = int(response['timestamp']) * 1000
    return Orderbook('coinone', equity_pair, asks, bids, timestamp)


class CoinoneException(Exception):
  pass


class CoinoneNonceException(CoinoneException):
  pass


class CoinoneUnknownCurrencyException(CoinoneException):
  pass
