# -*- coding: utf-8 -*-
from carbi.policy.fee import FeePolicy

BITFINEX_TAKER_FEE = 0.2 / 100


class BitfinexFeePolicy(FeePolicy):
  def __init__(self, config):
    self.config = config

  def get_effective_ratio(self, chain_node, ratio):
    return ratio

  def get_effective_fee(self, chain_node):
    return BITFINEX_TAKER_FEE

  def adjust_buy_volume(self, chain_node, volume):
    # TODO(Andrew): not implemented
    return volume
