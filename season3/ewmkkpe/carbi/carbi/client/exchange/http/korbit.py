# -*- coding: utf-8 -*-
import json

import requests

from carbi.client.exchange.pairs import ExchangeEquityPairs
from carbi.client.exchange.utils import public, validate_response
from carbi.struct.orderbook import Orderbook

EQUITY_PAIRS = ExchangeEquityPairs('korbit', pairs={
  'btc_krw': 'btc/krw',
  'eth_krw': 'eth/krw',
  'bch_krw': 'bch/krw',
  'xrp_krw': 'xrp/krw',
})


class KorbitClient(object):
  def __init__(self):
    pass

  @public
  def get_orderbook(self, equity_pair):
    """
    거래소의 Orderbook을 조회한다.
    Korbit의 경우 파라메터에 depth가 없다.
    :param equity_pair: eth/btc 와 같은 형태의 equity pair 문자열
    :return: Orderbook 객체
    """
    korbit_equity_pair = EQUITY_PAIRS.to_exchange_pair(equity_pair)
    url = 'https://api.korbit.co.kr/v1/orderbook'
    params = dict(
      currency_pair=korbit_equity_pair,
    )
    r = requests.get(url, params=params, timeout=5)
    response = json.loads(r.content)
    return KorbitParser.parse_orderbook_response(response, korbit_equity_pair)


class KorbitParser(object):
  @classmethod
  def parse_orderbook_response(cls, response, korbit_equity_pair):
    validate_response(response, required_keys=['asks', 'bids', 'timestamp'])
    assert len(response['asks']) != 0, 'INVALID_VALUE: orderbook:asks should not be empty'
    assert len(response['bids']) != 0, 'INVALID_VALUE: orderbook:bids should not be empty'
    equity_pair = EQUITY_PAIRS.from_exchange_pair(korbit_equity_pair)
    asks = map(lambda elem: {'price': float(elem[0]), 'volume': float(elem[1])}, response['asks'])
    bids = map(lambda elem: {'price': float(elem[0]), 'volume': float(elem[1])}, response['bids'])
    timestamp = int(response['timestamp'])
    return Orderbook('korbit', equity_pair, asks, bids, timestamp)


class KorbitException(Exception):
  pass
