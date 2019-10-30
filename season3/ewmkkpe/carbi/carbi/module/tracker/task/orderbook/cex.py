# -*- coding: utf-8 -*-

import gevent
from gevent.event import AsyncResult


class CexGetOrderBookTask(object):
  def __init__(self, injector, target):
    self.client = injector.cex_client
    self.channels = injector.channels
    self.target = target
    self.async_result = AsyncResult()

  def execute(self):
    gevent.spawn(self.get_orderbook)
    return self.async_result

  def get_orderbook(self):
    try:
      _, equity_pair = self.target.orderbook_key.split(':')
      channel = self.channels.get_channel_or_none('cex')
      orderbook = None
      if channel is not None:
        # 만약 Channel이 있다면 Channel을 통해 Orderbook을 가져와본다.
        orderbook = channel.get_orderbook_or_none(equity_pair=equity_pair, depth=20)
      if orderbook is None:
        # 만약 Channel을 통해 Orderbook을 가져오지 못했다면 HTTP로 시도해본다.
        orderbook = self.client.get_orderbook(equity_pair=equity_pair, depth=20)
      self.async_result.set(orderbook)
    except Exception as e:
      self.async_result.set_exception(e)
