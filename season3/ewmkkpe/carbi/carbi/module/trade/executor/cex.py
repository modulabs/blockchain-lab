# -*- coding: utf-8 -*-
import gevent

from carbi.client.exchange.http.cex import CexNonceException

NONCE_EXCEPTION_MAX_RETRY_COUNT = 10


class CexTradeExecutor(object):
  def __init__(self, injector):
    self.client = injector.cex_client
    self.channels = injector.channels
    self.logger = injector.logger

  def sell(self, equity_pair, price, volume):
    target_equity, base_equity = equity_pair.split('/')
    assert base_equity == 'usd'

    # 만약 Active한 WebSocket 채널이 있다면 채널을 이용해 거래한다.
    channel = self.channels.get_channel_or_none('cex')
    if channel is not None:
      self.logger.info('SELL cex:{0} {1:.5f} @ {2:.3f} '.format(target_equity, volume, price))
      channel.place_sell_order(equity_pair=equity_pair, amount=volume, price=price)
      return

    # 만약 Active한 웹소켓 연결이 없다면 HTTP로 거래를 시도해본다.
    max_retry_count = NONCE_EXCEPTION_MAX_RETRY_COUNT
    retry_count = 0
    while True:
      try:
        self.logger.info('SELL cex:{0} {1:.5f} @ {2:.3f} (http)'.format(target_equity, volume, price))
        self.client.place_sell_order(price=price, amount=volume, currency=target_equity)
        return
      except CexNonceException as cne:
        if retry_count < max_retry_count:
          self.logger.warn('CexNonceException: SELL({}) RetryCount : {}'.format(target_equity, retry_count))
          retry_count += 1
          gevent.sleep(0.1)
          continue
        raise
      except:
        raise

  def buy(self, equity_pair, price, volume):
    target_equity, base_equity = equity_pair.split('/')
    assert base_equity == 'usd'

    # 만약 Active한 웹소켓 채널이 있다면 채널을 이용해 거래한다.
    channel = self.channels.get_channel_or_none('cex')
    if channel is not None:
      self.logger.info('BUY cex:{0} {1:.5f} @ {2:.3f}'.format(target_equity, volume, price))
      channel.place_buy_order(equity_pair=equity_pair, amount=volume, price=price)
      return

    # 만약 Active한 웹소켓 연결이 없다면 HTTP로 거래를 시도해본다.
    max_retry_count = NONCE_EXCEPTION_MAX_RETRY_COUNT
    retry_count = 0
    while True:
      try:
        self.logger.info('BUY cex:{0} {1:.5f} @ {2:.3f} (http)'.format(target_equity, volume, price))
        self.client.place_buy_order(price=price, amount=volume, currency=target_equity)
        return
      except CexNonceException as cne:
        if retry_count < max_retry_count:
          self.logger.warn('CexNonceException: BUY({}) RetryCount : {}'.format(target_equity, retry_count))
          retry_count += 1
          gevent.sleep(0.1)
          continue
        raise
      except:
        raise
