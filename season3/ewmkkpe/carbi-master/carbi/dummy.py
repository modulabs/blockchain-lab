# -*- coding: utf-8 -*-
import sys

from carbi.struct.asset import Asset
from carbi.struct.context import BalanceContext
from carbi.utils import ts


def build_wealthy_balance_ctx(chains):
  balance_ctx = BalanceContext()
  equities = set()
  for chain in chains:
    # 현재 거래 리스트에 필요한 모든 equity를 만들어낸다.
    [equities.add(asset) for asset in chain.participating_equities(with_exchange=True)]
  assets = []
  for equity in equities:
    exchange, symbol = equity.split(':')
    volume = sys.maxint / 2
    assets.append(Asset(exchange, symbol, volume, ts()))
  for asset in assets:
    balance_ctx.assets[asset.key] = asset
  return balance_ctx
