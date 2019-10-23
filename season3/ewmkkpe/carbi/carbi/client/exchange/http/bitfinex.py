# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json

import requests

from carbi.client.exchange.nonce import NonceIssuer
from carbi.client.exchange.pairs import ExchangeEquityPairs
from carbi.client.exchange.utils import public, private, validate_response
from carbi.struct.orderbook import Orderbook

EQUITY_PAIRS = ExchangeEquityPairs('bitfinex', pairs={
  'BTCUSD': 'btc/usd',
  'ETHUSD': 'eth/usd',
  'BCHUSD': 'bch/usd',
  'XRPUSD': 'xrp/usd',
  'EOSUSD': 'eos/usd',
  'LTCUSD': 'ltc/usd',
  'ETCUSD': 'etc/usd',
  'BTGUSD': 'btg/usd',
})


class BitfinexConfiguration(object):
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
      config = BitfinexConfiguration()
      config.key = content['key']
      config.secret = content['secret']
      return config


class BitfinexClient(object):
  def __init__(self, conf):
    self.conf = conf
    self.nonce_issuer = NonceIssuer()

  def _get_payload(self, body):
    string = json.dumps(body)
    return base64.b64encode(string)

  def _get_signature(self, payload):
    return hmac.new(str(self.conf.secret), msg=payload, digestmod=hashlib.sha384).hexdigest()

  def _get_basic_private_headers(self, body):
    payload = self._get_payload(body)
    signature = self._get_signature(payload)
    return {
      'X-BFX-APIKEY': self.conf.key,
      'X-BFX-PAYLOAD': payload,
      'X-BFX-SIGNATURE': signature,
    }

  def _get_basic_private_body(self, path):
    return {
      'nonce': str(self.nonce_issuer.next_nonce()),
      'request': path,
    }

  def _make_url(self, path):
    return 'https://api.bitfinex.com' + path

  def _post(self, path, body):
    private_body = self._get_basic_private_body(path)
    body.update(private_body)

    url = self._make_url(path)
    headers = self._get_basic_private_headers(body)

    r = requests.get(url, headers=headers, timeout=5)
    return json.loads(r.content)

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
    bitfinex_equity_pair = EQUITY_PAIRS.to_exchange_pair(equity_pair)
    url = 'https://api.bitfinex.com/v1/book/{}'.format(bitfinex_equity_pair)
    params = dict(
      depth=depth,
    )
    r = requests.get(url, params=params, timeout=5)
    response = json.loads(r.content)
    return BitfinexParser.parse_orderbook_response(response, bitfinex_equity_pair)

  @private
  def get_balance(self):
    path = '/v1/balances'
    return self._post(path, {})

  @private
  def get_summary(self):
    path = '/v1/summary'
    return self._post(path, {})

  @private
  def get_margin_information(self):
    path = '/v1/margin_infos'
    return self._post(path, {})

  @private
  def get_active_positions(self):
    path = '/v1/positions'
    return self._post(path, {})


class BitfinexParser(Orderbook):
  @classmethod
  def parse_orderbook_response(cls, response, bitfinex_equity_pair):
    validate_response(response, required_keys=['asks', 'bids'])
    assert len(response['asks']) != 0, 'INVALID_VALUE: orderbook:asks should not be empty'
    assert len(response['bids']) != 0, 'INVALID_VALUE: orderbook:bids should not be empty'
    equity_pair = EQUITY_PAIRS.from_exchange_pair(bitfinex_equity_pair)
    asks = map(lambda elem: {'price': float(elem['price']), 'volume': float(elem['amount'])}, response['asks'])
    bids = map(lambda elem: {'price': float(elem['price']), 'volume': float(elem['amount'])}, response['bids'])
    timestamp = int(float(response['asks'][0]['timestamp']) * 1000)
    return Orderbook('bitfinex', equity_pair, asks, bids, timestamp)


class BitfinexException(Exception):
  pass
