# -*- coding: utf-8 -*-

import gevent
from gevent.event import AsyncResult


class OkexGetOrderBookTask(object):
  def __init__(self, injector, target):
    self.client = injector.okex_client
    self.logger = injector.logger
    self.target = target
    self.async_result = AsyncResult()

  def execute(self):
    gevent.spawn(self.get_orderbook)
    return self.async_result

  def get_orderbook(self):
    try:
      if self.target.type == 'spot':
        _, equity_pair = self.target.orderbook_key.split(':')
        orderbook = self.client.get_spot_orderbook(equity_pair=equity_pair)
        self.async_result.set(orderbook)
      elif self.target.type == 'future':
        equity_pair = self.target.equity_pair
        contract_type = self.target.contract_type
        orderbook = self.client.get_future_orderbook(equity_pair=equity_pair, contract_type=contract_type)
        self.async_result.set(orderbook)
    except Exception as e:
      self.async_result.set_exception(e)
