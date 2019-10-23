# -*- coding: utf-8 -*-


class BinanceTradeExecutor(object):
  def __init__(self, injector):
    self.client = injector.binance_client
    self.logger = injector.logger

  def sell(self, equity_pair, price, volume):
    target_equity, base_equity = equity_pair.split('/')
    assert base_equity in ['btc', 'eth', 'usdt', 'bnb']
    self.logger.info('SELL binance:{0} {1:.5f} @ {2:.3f}'.format(target_equity, volume, price))
    self.client.market_sell(equity_pair=equity_pair, volume=volume)

  def buy(self, equity_pair, price, volume):
    target_equity, base_equity = equity_pair.split('/')
    assert base_equity in ['btc', 'eth', 'usdt', 'bnb']
    self.logger.info('BUY binance:{0} {1:.5f} @ {2:.3f}'.format(target_equity, volume, price))
    self.client.market_buy(equity_pair=equity_pair, volume=volume)
