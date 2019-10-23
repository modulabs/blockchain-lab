# -*- coding: utf-8 -*-
import math
from datetime import datetime

import requests

from carbi.cmp import to_comparable_repr
from carbi.config import CarbiConfigKeys
from carbi.module.handler.struct import OrderbookSpread, TransferRatio, FuturePremium
from carbi.utils import datetime_kst, datetime_utc

OKEX_TOKENS = ['btc', 'ltc', 'eth', 'etc', 'bch', 'xrp', 'eos', 'btg']


class InspectMarketContextHandler(object):
  def __init__(self, injector, chains):
    self.injector = injector
    self.logger = injector.logger
    self.chains = chains
    self.last_sent = None

  def handle(self, market_ctx):
    lines = [
      '현 시각의 마켓 정보는 다음과 같습니다.',
      '```',
      'Future Premium',
      '',
      self.build_future_premium_text(market_ctx),
      '',
      'Transfer Premium',
      '',
      self.build_transfer_ratio_text(market_ctx),
      '',
      'Ask-Bid Spread',
      '',
      self.build_orderbook_spread_text(market_ctx),
      '',
      "KRW/USD: {0:.2f}".format(market_ctx.usd_krw_price),
      '',
      'TS(UTC): {}'.format(datetime_utc()),
      'TS(KST): {}'.format(datetime_kst()),
      '```',
    ]
    msg = '\n'.join(lines)
    self.notify(msg)
    self.logger.info(msg)

  def build_future_premium_text(self, market_ctx):
    future_premiums = [FuturePremium.build_future_premium(symbol, market_ctx) for symbol in OKEX_TOKENS]
    lines = []
    for future_premium in future_premiums:
      equity = future_premium.equity
      ratio = future_premium.ratio
      price_diff = future_premium.price_diff
      percentile = (ratio - 1) * 100
      diff = price_diff
      lines.append('{0:9}: {1:+.3f} % [{2:+.3f}]'.format(equity, percentile, diff))
    return '\n'.join(lines)

  def build_transfer_ratio_text(self, market_ctx):
    trade_ratios = [TransferRatio.build_transfer_ratio(chain, market_ctx) for chain in self.chains]
    trade_ratios = sorted(trade_ratios, key=lambda x: to_comparable_repr(x.exchange_pair + x.equity))

    last_exchange_pair = trade_ratios[0].exchange_pair
    lines = []
    for trade_ratio in trade_ratios:
      # exchange_pair가 바뀌었다면 한 줄 띄워준다.
      if last_exchange_pair != trade_ratio.exchange_pair:
        last_exchange_pair = trade_ratio.exchange_pair
        lines.append('')
      # TradeRatio에 대해 한줄씩 넣어준다.
      equity = trade_ratio.equity
      ratio = trade_ratio.ratio
      price_diff = trade_ratio.price_diff
      percentile = (ratio - 1) * 100
      log_percentile = 100 * math.log1p(ratio - 1)
      diff = int(price_diff)
      lines.append('{0:12}: {1:+.3f} % ({2:+.3f} ln%) [{3:+,d}]'.format(equity, percentile, log_percentile, diff))
    return '\n'.join(lines)

  def build_orderbook_spread_text(self, market_ctx):
    orderbook_spreads = OrderbookSpread.build_orderbook_spreads(self.chains, market_ctx)
    orderbook_spreads = sorted(orderbook_spreads, key=lambda x: to_comparable_repr(x.orderbook_key))

    last_exchange = orderbook_spreads[0].exchange
    lines = []
    for orderbook_spread in orderbook_spreads:
      # exchange가 바뀌었다면 한 줄 띄워준다.
      if last_exchange != orderbook_spread.exchange:
        last_exchange = orderbook_spread.exchange
        lines.append('')
      orderbook_key = orderbook_spread.orderbook_key
      spread_percentile = orderbook_spread.spread * 100
      lines.append('{0:16}: {1:.5f} %'.format(orderbook_key, spread_percentile))
    return '\n'.join(lines)

  def notify(self, text):
    if not self.should_notify_slack():
      return
    url = 'https://hooks.slack.com/services/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'
    payload = {
      'text': text,
    }
    requests.post(url, json=payload)
    self.last_sent = datetime.now()

  def should_notify_slack(self):
    if not self.injector.config[CarbiConfigKeys.SLACK_ENABLED]:
      return False
    now = datetime.now()
    if not self.last_sent:
      return True
    if self.last_sent.minute == now.minute:
      return False
    if now.minute % 5 == 0:
      return True
    return False
