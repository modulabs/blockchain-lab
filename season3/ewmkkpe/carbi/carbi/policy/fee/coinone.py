# -*- coding: utf-8 -*-
from carbi.config import CarbiConfigKeys
from carbi.policy.fee import FeePolicy


class CoinoneFeePolicy(FeePolicy):
  def __init__(self, config):
    self.config = config

  def get_effective_ratio(self, chain_node, ratio):
    return ratio

  def get_effective_fee(self, chain_node):
    return self._get_taker_fee()

  def adjust_buy_volume(self, chain_node, volume):
    # 코인원의 경우 거래할때 수수료까지 포함해서 주문을 넣어야한다.
    # 이를 위해 volume을 수수료만큼 조정해줘야한다.
    return volume / (1 - self._get_taker_fee())

  def _get_taker_fee(self):
    return self.config[CarbiConfigKeys.COINONE_TAKER_FEE] / 100
