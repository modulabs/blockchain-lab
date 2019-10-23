# -*- coding: utf-8 -*-
from carbi.module.trade.executor import cex, coinone, binance


class TradeExecutorFactory(object):
  def __init__(self, injector):
    self.injector = injector

  def get_executor(self, exchange):
    if exchange == 'cex':
      return cex.CexTradeExecutor(self.injector)
    elif exchange == 'coinone':
      return coinone.CoinoneTradeExecutor(self.injector)
    elif exchange == 'binance':
      return binance.BinanceTradeExecutor(self.injector)

    # 아직 구현되지 않았으면 Exception을 던진다.
    raise NotImplementedError("trade_executor for {} is not implemented.".format(exchange))
