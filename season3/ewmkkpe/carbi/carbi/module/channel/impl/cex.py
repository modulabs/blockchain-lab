# -*- coding: utf-8 -*-
import sys
from carbi.client.exchange.http.cex import EQUITY_PAIRS
from carbi.client.exchange.utils import public, private, callback
from carbi.client.exchange.websocket.cex import CexWebSocketClient
from carbi.module.channel.impl import Channel
from carbi.module.trade.chain import get_orderbook_keys


class CexChannel(Channel):
  def __init__(self, injector):
    client = CexWebSocketClient(injector.credentials.cex, injector.logger)
    Channel.__init__(self, injector, client)
    self.client.on_active = self.on_active
    self.client.on_error = self.on_error
    self.client.on_close = self.on_close
    self.logger = injector.logger
    self.equity_pairs = []

  @callback
  def on_active(self, ws):
    self._notify_active()
    # 인증이 성공하면 Orderbook을 Subscribe한다.
    self.logger.info('CEX_CHANNEL: subscribe: {}'.format(self.equity_pairs))
    supported_equity_pairs = filter(lambda p: EQUITY_PAIRS.is_supported_equity_pair(p), self.equity_pairs)
    for equity_pair in supported_equity_pairs:
      self.client.subscribe_orderbook(equity_pair=equity_pair)

  @callback
  def on_error(self, ws, error):
    self.logger.warn('CEX_CHANNEL: channel got error.')
    self.logger.warn(error, exc_info=sys.exc_info())

  @callback
  def on_close(self, ws):
    self.logger.warn('CEX_CHANNEL: websocket connection closed.')

  @public
  def get_orderbook_or_none(self, equity_pair, depth=20):
    try:
      return self.client.get_orderbook(equity_pair=equity_pair, depth=depth)
    except:
      return None

  @private
  def place_buy_order(self, equity_pair, amount, price):
    return self.client.place_buy_order(equity_pair, amount, price)

  @private
  def place_sell_order(self, equity_pair, amount, price):
    return self.client.place_sell_order(equity_pair, amount, price)

  @staticmethod
  def build(injector, chains):
    orderbook_keys = get_orderbook_keys(chains)
    cex_orderbook_keys = filter(lambda x: x.split(':')[0] == 'cex', orderbook_keys)
    cex_equity_pairs = map(lambda x: x.split(':')[1], cex_orderbook_keys)
    channel = CexChannel(injector)
    channel.equity_pairs = cex_equity_pairs
    return channel
