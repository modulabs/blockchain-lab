# -*- coding: utf-8 -*-
import yaml
from carbi.module.trade.chain import TradeChainNode
from carbi.module.balancer.task import BalancingTask


class BalancingRules(object):
  def __init__(self):
    pass

  @classmethod
  def load_rules(cls, config_file_path):
    with open(config_file_path, 'rU') as f:
      config = yaml.load(f)

      rules = []
      if 'total_volume_balancing_rules' in config:
        for rule_config in config['total_volume_balancing_rules']:
          equity = rule_config['equity']
          volume = rule_config['volume']
          minimum_transfer_volume = rule_config['minimum_transfer_volume']
          exchange = rule_config['exchange']
          trading_equity_pair = rule_config['trading_equity_pair']

          rule = TotalVolumeBalancingRule(equity, volume, minimum_transfer_volume, exchange, trading_equity_pair)
          rules.append(rule)

      if 'minimum_volume_balancing_rules' in config:
        for rule_config in config['minimum_volume_balancing_rules']:
          equity = rule_config['equity']
          target_volume = rule_config['target_volume']
          threshold_volume = rule_config['threshold_volume']
          exchange = rule_config['exchange']
          trading_equity_pair = rule_config['trading_equity_pair']

          rule = MinimumVolumeBalancingRule(equity, target_volume, threshold_volume, exchange, trading_equity_pair)
          rules.append(rule)
    return rules


class BalancingRule(object):
  def __init__(self, equity, exchange, trading_equity_pair):
    self.equity = equity
    self.exchange = exchange
    self.trading_equity_pair = trading_equity_pair

  def balancing_task(self, current_volume):
    balancing_volume = self.required_balancing_volume(current_volume)

    if balancing_volume == 0:
      # Nothing to do
      return None
    else:
      chain_node = TradeChainNode()
      chain_node.exchange = self.exchange
      target_equity, base_equity = self.trading_equity_pair.split("/")
      chain_node.target_equity = target_equity
      chain_node.base_equity = base_equity

      if balancing_volume > 0:
        chain_node.action = 'buy'
        return BalancingTask(chain_node, balancing_volume, self)
      else:
        chain_node.action = 'sell'
        return BalancingTask(chain_node, abs(balancing_volume), self)

  def required_balancing_volume(self, current_volume):
    raise NotImplementedError()

  @property
  def balancing_task_target_volume(self):
    raise NotImplementedError()


class TotalVolumeBalancingRule(BalancingRule):
  def __init__(self, equity, volume, minimum_transfer_volume, exchange, trading_equity_pair):
    super(TotalVolumeBalancingRule, self).__init__(equity, exchange, trading_equity_pair)
    self.volume = volume
    self.minimum_transfer_volume = minimum_transfer_volume

  def required_balancing_volume(self, current_volume):
    diff = self.volume - current_volume
    if diff < 0:
      # diff 만큼 팔아야 됨
      return diff

    if 0 <= diff < self.minimum_transfer_volume:
      # diff 만큼 사야 됨
      return diff

    # 이 경우는 코인 중 일부가 transfering 하고 있는 상태일 수가 있으므로, 아무것도 하지 않습니다.
    return 0

  @property
  def balancing_task_target_volume(self):
    return self.volume


class MinimumVolumeBalancingRule(BalancingRule):
  def __init__(self, equity, target_volume, threshold_volume, exchange, trading_equity_pair):
    super(MinimumVolumeBalancingRule, self).__init__(equity, exchange, trading_equity_pair)
    self.target_volume = target_volume
    self.threshold_volume = threshold_volume

  def required_balancing_volume(self, current_volume):
    if current_volume < self.threshold_volume:
      return self.target_volume - current_volume
    return 0

  @property
  def balancing_task_target_volume(self):
    return self.target_volume
