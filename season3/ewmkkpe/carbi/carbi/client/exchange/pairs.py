# -*- coding: utf-8 -*-


def _build_reverse_mapper(pairs):
  reverse_mapper = {}
  for p in pairs:
    reverse_mapper[pairs[p]] = p
  return reverse_mapper


class ExchangeEquityPairs(object):
  def __init__(self, exchange, pairs):
    self.exchange = exchange
    self.mapper = pairs
    self.reverse_mapper = _build_reverse_mapper(pairs)

  def from_exchange_pair(self, exchange_equity_pair):
    assert exchange_equity_pair in self.mapper, 'UNKNOWN_PAIR[exchange={}]: {}'.format(self.exchange, exchange_equity_pair)
    return self.mapper[exchange_equity_pair]

  def to_exchange_pair(self, equity_pair):
    assert equity_pair in self.reverse_mapper, 'UNKNOWN_PAIR[exchange={}]: {}'.format(self.exchange, equity_pair)
    return self.reverse_mapper[equity_pair]

  def is_supported_equity_pair(self, equity_pair):
    return equity_pair in self.reverse_mapper
