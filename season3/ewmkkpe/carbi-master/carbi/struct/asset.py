# -*- coding: utf-8 -*-


class Asset(object):
  def __init__(self, exchange, equity, volume, timestamp):
    self.exchange = exchange
    self.equity = equity
    self.volume = volume
    self.timestamp = timestamp

  @property
  def key(self):
    return '%s:%s' % (self.exchange, self.equity)

  def __str__(self):
    return "Asset(%s:%s %s)" % (self.exchange, self.equity, self.volume)

  def __repr__(self):
    return self.__str__()
