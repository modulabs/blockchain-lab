# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import time
import urllib

import requests

from carbi.client.exchange import constants
from carbi.client.exchange.pairs import ExchangeEquityPairs
from carbi.client.exchange.utils import public, private, validate_response
from carbi.struct.orderbook import Orderbook

EQUITY_PAIRS = ExchangeEquityPairs('poloniex', pairs={
  'USDT_REP': 'rep/usdt',
  'BTC_CVC': 'cvc/btc',
  'BTC_XVC': 'xvc/btc',
  'BTC_PINK': 'pink/btc',
  'BTC_SYS': 'sys/btc',
  'BTC_EMC2': 'emc2/btc',
  'BTC_RADS': 'rads/btc',
  'BTC_SC': 'sc/btc',
  'BTC_MAID': 'maid/btc',
  'BTC_BCH': 'bch/btc',
  'BTC_GNT': 'gnt/btc',
  'BTC_BCN': 'bcn/btc',
  'BTC_REP': 'rep/btc',
  'BTC_BCY': 'bcy/btc',
  'BTC_GNO': 'gno/btc',
  'XMR_NXT': 'nxt/xmr',
  'USDT_ZEC': 'zec/usdt',
  'BTC_FCT': 'fct/btc',
  'BTC_GAS': 'gas/btc',
  'USDT_ETH': 'eth/usdt',
  'USDT_BTC': 'btc/usdt',
  'BTC_LBC': 'lbc/btc',
  'BTC_DCR': 'dcr/btc',
  'USDT_ETC': 'etc/usdt',
  'ETH_OMG': 'omg/eth',
  'BTC_AMP': 'amp/btc',
  'BTC_XPM': 'xpm/btc',
  'BTC_NXT': 'nxt/btc',
  'BTC_VTC': 'vtc/btc',
  'ETH_STEEM': 'steem/eth',
  'XMR_BLK': 'blk/xmr',
  'BTC_PASC': 'pasc/btc',
  'XMR_ZEC': 'zec/xmr',
  'BTC_GRC': 'grc/btc',
  'BTC_NXC': 'nxc/btc',
  'BTC_BTCD': 'btcd/btc',
  'BTC_LTC': 'ltc/btc',
  'BTC_DASH': 'dash/btc',
  'BTC_STORJ': 'storj/btc',
  'ETH_ZEC': 'zec/eth',
  'BTC_ZEC': 'zec/btc',
  'BTC_BURST': 'burst/btc',
  'ETH_ZRX': 'zrx/eth',
  'BTC_BELA': 'bela/btc',
  'BTC_STEEM': 'steem/btc',
  'BTC_ETC': 'etc/btc',
  'BTC_ETH': 'eth/btc',
  'BTC_HUC': 'huc/btc',
  'BTC_STRAT': 'strat/btc',
  'BTC_LSK': 'lsk/btc',
  'BTC_EXP': 'exp/btc',
  'BTC_CLAM': 'clam/btc',
  'ETH_REP': 'rep/eth',
  'XMR_DASH': 'dash/xmr',
  'ETH_CVC': 'cvc/eth',
  'USDT_BCH': 'bch/usdt',
  'BTC_ZRX': 'zrx/btc',
  'USDT_DASH': 'dash/usdt',
  'BTC_BLK': 'blk/btc',
  'BTC_XRP': 'xrp/btc',
  'USDT_NXT': 'nxt/usdt',
  'BTC_NEOS': 'neos/btc',
  'BTC_OMG': 'omg/btc',
  'BTC_BTS': 'bts/btc',
  'BTC_DOGE': 'doge/btc',
  'ETH_GNT': 'gnt/eth',
  'BTC_SBD': 'sbd/btc',
  'ETH_GNO': 'gno/eth',
  'BTC_XCP': 'xcp/btc',
  'USDT_LTC': 'ltc/usdt',
  'BTC_BTM': 'btm/btc',
  'USDT_XMR': 'xmr/usdt',
  'ETH_LSK': 'lsk/eth',
  'BTC_OMNI': 'omni/btc',
  'BTC_NAV': 'nav/btc',
  'BTC_FLDC': 'fldc/btc',
  'ETH_BCH': 'bch/eth',
  'BTC_XBC': 'xbc/btc',
  'BTC_DGB': 'dgb/btc',
  'XMR_BTCD': 'btcd/xmr',
  'BTC_VRC': 'vrc/btc',
  'BTC_RIC': 'ric/btc',
  'XMR_MAID': 'maid/xmr',
  'BTC_STR': 'str/btc',
  'BTC_POT': 'pot/btc',
  'BTC_XMR': 'xmr/btc',
  'BTC_VIA': 'via/btc',
  'BTC_XEM': 'xem/btc',
  'BTC_NMC': 'nmc/btc',
  'ETH_ETC': 'etc/eth',
  'XMR_LTC': 'ltc/xmr',
  'BTC_ARDR': 'ardr/btc',
  'ETH_GAS': 'gas/eth',
  'BTC_FLO': 'flo/btc',
  'USDT_XRP': 'xrp/usdt',
  'BTC_GAME': 'game/btc',
  'BTC_PPC': 'ppc/btc',
  'XMR_BCN': 'bcn/xmr',
  'USDT_STR': 'str/usdt',
})


class PoloniexConfiguration(object):
  __slots__ = (
    'api_key',
    'secret',
  )

  def __repr__(self):
    return json.dumps(self.__dict__, indent=2)

  @staticmethod
  def load_from_file(config_file):
    with open(config_file, "r") as f:
      content = json.load(f)
      config = PoloniexConfiguration()
      config.api_key = content['api_key']
      config.secret = content['secret']
      return config


class PoloniexClient(object):
  def __init__(self, conf):
    self.conf = conf

  @staticmethod
  def trade_url():
    return 'https://poloniex.com/tradingApi'

  def preprocess_payload(self, command, payload):
    payload[u'command'] = command
    # add nonce, TODO: change to read/write this value to permanent file
    payload[u'nonce'] = int(time.time() * 1000)
    return urllib.urlencode(payload)

  def get_signature(self, processed_payload):
    signature = hmac.new(str(self.conf.secret), processed_payload, hashlib.sha512);
    return signature.hexdigest()

  def trade_api(self, command, payload):
    processed_payload = self.preprocess_payload(command, payload)
    headers = {
      'Content-type': 'application/x-www-form-urlencoded',
      'User-Agent': constants.USER_AGENT,
      'Key': self.conf.api_key,
      'Sign': self.get_signature(processed_payload)
    }

    r = requests.post(PoloniexClient.trade_url(), headers=headers, data=processed_payload, timeout=10)
    return json.loads(r.content)

  @public
  def get_orderbook(self, equity_pair, depth=20):
    """
    거래소의 Orderbook을 조회한다.
    :param equity_pair: eth/btc 와 같은 형태의 equity pair 문자열
    :param depth: 조회할 Orderbook의 depth
    :return: Orderbook 객체
    """
    # https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_ETH&depth=10
    poloniex_currency_pair = EQUITY_PAIRS.to_exchange_pair(equity_pair)
    url = 'https://poloniex.com/public'
    params = {
      'command': 'returnOrderBook',
      'currencyPair': poloniex_currency_pair,
      'depth': depth,
    }
    headers = {
      'Content-type': 'application/json',
      'User-Agent': constants.USER_AGENT,
    }
    r = requests.get(url=url, headers=headers, params=params, timeout=5)
    response = json.loads(r.content)
    return PoloniexParser.parse_orderbook_response(response, poloniex_currency_pair)

  @private
  def return_balances(self):
    return self.trade_api('returnBalances', {})

  @private
  def buy_order(self, currency_pair, rate, amount, option=None):
    return self.buy_or_sell_order('buy', currency_pair, rate, amount, option)

  @private
  def sell_order(self, currency_pair, rate, amount, option=None):
    return self.buy_or_sell_order('sell', currency_pair, rate, amount, option)

  @private
  def buy_or_sell_order(self, command, currency_pair, rate, amount, option):
    """
    You may optionally set "fillOrKill", "immediateOrCancel", "postOnly" to 1.
    fillOrKill - 무조건 전부 계약이 되거나 아니면 전부 계약이 안되거나 옵션
    immediateOrCancel - 일단 해당 가격에 계약 시킬 수 있을 만큼 계약시키고 나머지는 버림
    postOnly - 무조건 계약이 안되고 orderbook에만 남아야 함. Taker 수수료를 안내고 Maker 수수료를 낼 수 있도록 보장해줌
    """
    payload = {"currencyPair": currency_pair, "rate": rate, "amount": amount}

    if option is not None and option in ["fillOrKill", "immediateOrCancel", "postOnly"]:
      payload[option] = 1

    return self.trade_api(command, payload)


class PoloniexParser(object):
  @classmethod
  def parse_orderbook_response(cls, response, poloniex_currency_pair):
    validate_response(response, required_keys=['asks', 'bids', 'timestamp'])
    assert len(response['asks']) != 0, 'INVALID_VALUE: orderbook:asks should not be empty'
    assert len(response['bids']) != 0, 'INVALID_VALUE: orderbook:bids should not be empty'
    equity_pair = EQUITY_PAIRS.from_exchange_pair(poloniex_currency_pair)
    asks = map(lambda elem: {'price': float(elem[0]), 'volume': float(elem[1])}, response['asks'])
    bids = map(lambda elem: {'price': float(elem[0]), 'volume': float(elem[1])}, response['bids'])
    timestamp = int(response['timestamp']) * 1000
    return Orderbook('poloniex', equity_pair, asks, bids, timestamp)


class PoloniexException(Exception):
  pass
