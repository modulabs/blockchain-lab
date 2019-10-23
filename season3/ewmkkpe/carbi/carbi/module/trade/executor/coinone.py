# -*- coding: utf-8 -*-
import gevent

from carbi.client.exchange.http.coinone import CoinoneNonceException

NONCE_EXCEPTION_MAX_RETRY_COUNT = 10


class CoinoneTradeExecutor(object):
  def __init__(self, injector):
    self.client = injector.coinone_client
    self.logger = injector.logger

  def sell(self, equity_pair, price, volume):
    target_equity, base_equity = equity_pair.split('/')
    assert base_equity == 'krw'
    max_retry_count = NONCE_EXCEPTION_MAX_RETRY_COUNT
    retry_count = 0
    while True:
      try:
        self.logger.info('SELL coinone:{0} {1:.5f} @ {2:.3f}'.format(target_equity, volume, price))
        self.client.sell_limit(target_equity, price, volume)
        return
      except CoinoneNonceException as cne:
        if retry_count < max_retry_count:
          self.logger.warn('CoinoneNonceException: SELL({}) RetryCount : {}'.format(target_equity, retry_count))
          retry_count += 1
          gevent.sleep(0.1)
          continue
        raise
      except:
        raise

  def buy(self, equity_pair, price, volume):
    target_equity, base_equity = equity_pair.split('/')
    assert base_equity == 'krw'
    max_retry_count = NONCE_EXCEPTION_MAX_RETRY_COUNT
    retry_count = 0
    while True:
      try:
        self.logger.info('BUY coinone:{0} {1:.5f} @ {2:.3f}'.format(target_equity, volume, price))
        self.client.buy_limit(target_equity, price, volume)
        return
      except CoinoneNonceException as cne:
        if retry_count < max_retry_count:
          self.logger.warn('CoinoneNonceException: BUY({}) RetryCount : {}'.format(target_equity, retry_count))
          retry_count += 1
          gevent.sleep(0.1)
          continue
        raise
      except:
        raise
