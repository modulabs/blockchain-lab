# -*- coding: utf-8 -*-
from carbi.config import CarbiConfigKeys
from carbi.policy.fee import FeePolicy


class KorbitFeePolicy(FeePolicy):
  def __init__(self, config):
    self.config = config

  def get_effective_ratio(self, chain_node, ratio):
    return ratio

  def get_effective_fee(self, chain_node):
    return self._get_taker_fee()

  def adjust_buy_volume(self, chain_node, volume):
    # TODO(Andrew): not implemented
    return volume

  def _get_taker_fee(self):
    return self.config[CarbiConfigKeys.KORBIT_TAKER_FEE] / 100
