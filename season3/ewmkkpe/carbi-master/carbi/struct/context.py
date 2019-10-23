# -*- coding: utf-8 -*-


class MarketContext(object):
  def __init__(self):
    self.orderbooks = dict()
    self.currency_exchange_rates = dict()

  @property
  def usd_krw_price(self):
    currency_rates = self.currency_exchange_rates
    return currency_rates['krw/usd'].rate

  def bid0_price(self, orderbook_key):
    assert orderbook_key in self.orderbooks, 'ORDERBOOK_NOT_FOUND: {}'.format(orderbook_key)
    orderbook = self.orderbooks[orderbook_key]
    return orderbook.bid0_price

  def ask0_price(self, orderbook_key):
    assert orderbook_key in self.orderbooks, 'ORDERBOOK_NOT_FOUND: {}'.format(orderbook_key)
    orderbook = self.orderbooks[orderbook_key]
    return orderbook.ask0_price

  def __str__(self):
    return "MarketContext(%s)" % self.orderbooks

  def __repr__(self):
    return self.__str__()


class BalanceContext(object):
  def __init__(self):
    self.assets = dict()

  def __str__(self):
    return "BalanceContext(%s)" % self.assets

  def __repr__(self):
    return self.__str__()
