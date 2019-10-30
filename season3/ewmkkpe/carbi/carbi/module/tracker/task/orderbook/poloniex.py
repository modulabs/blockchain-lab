# -*- coding: utf-8 -*-

import gevent
from gevent.event import AsyncResult


class PoloniexGetOrderBookTask(object):
  def __init__(self, injector, target):
    self.client = injector.poloniex_client
    self.target = target
    self.async_result = AsyncResult()

  def execute(self):
    gevent.spawn(self.get_orderbook)
    return self.async_result

  def get_orderbook(self):
    try:
      _, equity_pair = self.target.orderbook_key.split(':')
      orderbook = self.client.get_orderbook(equity_pair=equity_pair, depth=20)
      self.async_result.set(orderbook)
    except Exception as e:
      self.async_result.set_exception(e)
