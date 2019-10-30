# -*- coding: utf-8 -*-
from carbi.config import CarbiConfigKeys
from carbi.policy.fee import FeePolicy


class CexFeePolicy(FeePolicy):
  def __init__(self, config):
    self.config = config

  def get_effective_ratio(self, chain_node, ratio):
    assert chain_node.action in ['buy', 'sell']
    if chain_node.action == 'buy':
      return ratio / (1 + self._get_taker_fee())
    elif chain_node.action == 'sell':
      return ratio
    else:
      return ratio

  def get_effective_fee(self, chain_node):
    assert chain_node.action in ['buy', 'sell']
    if chain_node.action == 'buy':
      return 0
    elif chain_node.action == 'sell':
      return self._get_taker_fee()
    else:
      return 0

  def adjust_buy_volume(self, chain_node, volume):
    # cex의 경우 수수료는 usd로 나가기 때문에 따로 처리할 필요 없이 바로 거래하면 된다.
    return volume

  def _get_taker_fee(self):
    return self.config[CarbiConfigKeys.CEX_TAKER_FEE] / 100
