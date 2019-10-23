# -*- coding: utf-8 -*-
from carbi.config import CarbiConfigKeys
from carbi.policy.fee import FeePolicy


class BinanceFeePolicy(FeePolicy):
  def __init__(self, config):
    self.config = config

  def get_effective_ratio(self, chain_node, ratio):
    return ratio

  def get_effective_fee(self, chain_node):
    if self.bnb_fee_deduct_enabled():
      # # XXX(Andrew): 일단 임시로 이렇게 구현합니다. 이렇게 구현하면 이득을 과대 추정하는 문제가 있긴 하지만, crypto balance가 서서히 증가하는 문제는 없어집니다.
      return 0
    else:
      return self._get_taker_fee()

  def adjust_buy_volume(self, chain_node, volume):
    if self.bnb_fee_deduct_enabled():
      return volume
    else:
      # same pattern with coinone/poloniex
      return volume / (1 - self._get_taker_fee())

  def _get_taker_fee(self):
    bnb_fee_deduct_multiplier = 1
    if self.bnb_fee_deduct_enabled():
      bnb_fee_deduct_multiplier = 0.5

    taker_fee = self.config[CarbiConfigKeys.BINANCE_TAKER_FEE] / 100
    return taker_fee * bnb_fee_deduct_multiplier

  def bnb_fee_deduct_enabled(self):
    return self.config[CarbiConfigKeys.BINANCE_BNB_FEE_DEDUCT_ENABLED]
