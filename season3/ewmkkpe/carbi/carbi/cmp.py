# -*- coding: utf-8 -*-

EXCHANGE_ORDER = ['coinone', 'korbit', 'upbit', 'bitfinex', 'cex', 'binance', 'poloniex']
EQUITY_ORDER = ['btc', 'eth', 'bch', 'xrp', 'bnb', 'usd', 'usdt', 'krw']


def to_comparable_repr(value):
  comparable_repr = value
  for exchange in EXCHANGE_ORDER:
    idx = EXCHANGE_ORDER.index(exchange)
    comparable_repr = comparable_repr.replace(exchange, '!{0:012d}'.format(idx))
  for equity in EQUITY_ORDER:
    idx = EQUITY_ORDER.index(equity)
    comparable_repr = comparable_repr.replace(equity, '!{0:012d}'.format(idx))
  return comparable_repr
