# -*- coding: utf-8 -*-
from carbi.utils.lines import ContentLines
from carbi.utils import datetime_kst, datetime_utc
from carbi.cmp import to_comparable_repr


class NotifyBalanceStatusMessageContent(object):
  def __init__(self, market_ctx, balance_ctx):
    self.market_ctx = market_ctx
    self.balance_ctx = balance_ctx

  @property
  def title(self):
    return '현재 편드의 현황은 다음과 같습니다.'

  @property
  def text(self):
    return self._build_text()

  def _build_text(self):
    texts = [
      "Balance Status",
      "",
      "{}".format(self._build_balance_status_text()),
      "",
      "Fiat Value: {0:,.0f} KRW".format(self._build_asset_value()),
      "Total Value: x KRW",
      "Total NominalValue: x KRW",
      "KRW/USD: {0:.2f}".format(self.market_ctx.usd_krw_price),
      "",
      "Time(UTC) : {}".format(datetime_utc()),
      "Time(KST) : {}".format(datetime_kst()),
    ]
    return "\n".join(texts)

  def _build_balance_status_text(self):
    asset_volumes = self._total_asset_volumes().items()
    asset_volumes = sorted(asset_volumes, key=lambda x: to_comparable_repr(x[0]))
    texts = []
    for (equity, volume) in asset_volumes:
      texts.append(ContentLines.get_balance_line(equity, volume))
    return '\n'.join(texts)

  def _build_asset_value(self):
    asset_volumes = self._total_asset_volumes()
    usd_krw_price = self.market_ctx.usd_krw_price
    bnb_usd_price = self.market_ctx.bid0_price('binance:bnb/usdt')

    value = 0
    if 'krw' in asset_volumes:
      value += asset_volumes['krw']
    if 'usd' in asset_volumes:
      value += asset_volumes['usd'] * usd_krw_price
    if 'usdt' in asset_volumes:
      value += asset_volumes['usdt'] * usd_krw_price
    if 'bnb' in asset_volumes:
      value += asset_volumes['bnb'] * bnb_usd_price * usd_krw_price
    return value

  def _total_asset_volumes(self):
    asset_volumes = dict()
    for (key, asset) in self.balance_ctx.assets.iteritems():
      _, equity = key.split(':')
      if equity not in asset_volumes:
        asset_volumes[equity] = 0
      asset_volumes[equity] += asset.volume
    return asset_volumes
