# -*- coding: utf-8 -*-

from carbi.module.tracker.task.orderbook import cex, coineone, poloniex, bitfinex, korbit, binance, okex


def get_orderbook_task(injector, target):
  exchange = target.exchange
  if exchange == 'cex':
    return cex.CexGetOrderBookTask(injector, target)
  elif exchange == 'coinone':
    return coineone.CoinoneGetOrderBookTask(injector, target)
  elif exchange == 'poloniex':
    return poloniex.PoloniexGetOrderBookTask(injector, target)
  elif exchange == 'bitfinex':
    return bitfinex.BitfinexGetOrderBookTask(injector, target)
  elif exchange == 'korbit':
    return korbit.KorbitGetOrderBookTask(injector, target)
  elif exchange == 'binance':
    return binance.BinanceGetOrderBookTask(injector, target)
  elif exchange == 'okex':
    return okex.OkexGetOrderBookTask(injector, target)
  raise NotImplementedError("GetOrderbookTask for {} is not implemented.".format(target))
