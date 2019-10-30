# -*- coding: utf-8 -*-
import json
import math


def _build_volume_policies(injector):
  volume_policies = dict()

  volume_policies['coinone'] = VolumePolicy.build(injector, 'conf/policies/coinone.json')
  volume_policies['cex'] = VolumePolicy.build(injector, 'conf/policies/cex.json')
  volume_policies['binance'] = VolumePolicy.build(injector, 'conf/policies/binance.json')
  volume_policies['korbit'] = DummyVolumePolicy(injector)
  volume_policies['bitfinex'] = DummyVolumePolicy(injector)
  return volume_policies


class VolumePolicyProvider(object):
  def __init__(self, injector):
    self.volume_policies = _build_volume_policies(injector)

  def get_policy(self, exchange):
    assert exchange in self.volume_policies
    return self.volume_policies[exchange]


class VolumePolicy(object):
  def __init__(self, injector, rules):
    self.injector = injector
    self.rules = rules

  def floor_volume(self, equity_pair, volume):
    assert equity_pair in self.rules, "equity_pair {} should be member of rules.".format(equity_pair)
    volume_min = self.rules[equity_pair].min
    volume_max = self.rules[equity_pair].max
    volume_step = self.rules[equity_pair].step

    if volume_min is not None and volume < volume_min:
      return 0

    if volume_max is not None and volume > volume_max:
      return volume_max

    if volume_step is not None:
      # floating point 소수점 이하 precision 문제 때문에 이렇게 하는 게 좀 더 정확할 것 같습니다.
      if volume_step <= 1:
        volume_multiplier = 1 / volume_step
        return math.floor(float(volume) * volume_multiplier) / volume_multiplier
      else:
        return volume_step * math.floor(float(volume) / volume_step)

    return volume

  @staticmethod
  def build(injector, config_path):
    rules = VolumePolicy.parse_rules(config_path)
    return VolumePolicy(injector, rules)

  @staticmethod
  def parse_rules(config_path):
    with open(config_path, 'rU') as f:
      conf = json.load(f)

      rules = {}
      for equity_pair in conf:
        min = None
        max = None
        step = None
        if 'volume' in conf[equity_pair]:
          volume_conf = conf[equity_pair]['volume']
          if 'min' in volume_conf:
            min = volume_conf['min']
          if 'max' in volume_conf:
            max = volume_conf['max']
          if 'step' in volume_conf:
            step = volume_conf['step']

        volume_rule = VolumeRule(min, max, step)
        rules[equity_pair] = volume_rule
      return rules


class DummyVolumePolicy(VolumePolicy):
  def __init__(self, injector):
    super(DummyVolumePolicy, self).__init__(injector, {})

  def floor_volume(self, equity_pair, volume):
    return volume


class VolumeRule(object):
  def __init__(self, min, max, step):
    self.min = min
    self.max = max
    self.step = step
