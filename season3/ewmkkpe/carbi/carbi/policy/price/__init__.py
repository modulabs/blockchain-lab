# -*- coding: utf-8 -*-
import json
import math


def _build_price_policies(injector):
  price_policies = dict()

  price_policies['coinone'] = PricePolicy.build(injector, 'conf/policies/coinone.json')
  price_policies['cex'] = PricePolicy.build(injector, 'conf/policies/cex.json')
  price_policies['binance'] = PricePolicy.build(injector, 'conf/policies/binance.json')
  price_policies['korbit'] = DummyPricePolicy(injector)
  price_policies['bitfinex'] = DummyPricePolicy(injector)
  return price_policies


class PricePolicyProvider(object):
  def __init__(self, injector):
    self.price_policies = _build_price_policies(injector)

  def get_policy(self, exchange):
    assert exchange in self.price_policies
    return self.price_policies[exchange]


class PricePolicy(object):
  def __init__(self, injector, rules):
    self.injector = injector
    self.rules = rules

  def floor_price(self, equity_pair, price):
    assert equity_pair in self.rules, "equity_pair {} should be member of rules.".format(equity_pair)
    price_min = self.rules[equity_pair].min
    price_max = self.rules[equity_pair].max
    price_step = self.rules[equity_pair].step

    if price_min is not None and price < price_min:
      return 0

    if price_max is not None and price > price_max:
      return price_max

    if price_step is not None:
      if price_step <= 1:
        price_multiplier = 1 / price_step
        return math.floor(float(price) * price_multiplier) / price_multiplier
      else:
        return price_step * math.floor(float(price) / price_step)

    return price

  def ceil_price(self, equity_pair, price):
    assert equity_pair in self.rules, "equity_pair {} should be member of rules.".format(equity_pair)
    price_min = self.rules[equity_pair].min
    price_max = self.rules[equity_pair].max
    price_step = self.rules[equity_pair].step

    if price_min is not None and price < price_min:
      return price_min

    if price_max is not None and price > price_max:
      # probably raise exception?
      return price_max

    if price_step is not None:
      if price_step <= 1:
        price_multiplier = 1 / price_step
        return math.ceil(float(price) * price_multiplier) / price_multiplier
      else:
        return price_step * math.ceil(float(price) / price_step)

    return price

  @staticmethod
  def build(injector, config_path):
    rules = PricePolicy.parse_rules(config_path)
    return PricePolicy(injector, rules)

  @staticmethod
  def parse_rules(config_path):
    with open(config_path, 'rU') as f:
      conf = json.load(f)

      rules = {}
      for equity_pair in conf:
        min = None
        max = None
        step = None
        if 'price' in conf[equity_pair]:
          price_conf = conf[equity_pair]['price']
          if 'min' in price_conf:
            min = price_conf['min']
          if 'max' in price_conf:
            max = price_conf['max']
          if 'step' in price_conf:
            step = price_conf['step']

        price_rule = PriceRule(min, max, step)
        rules[equity_pair] = price_rule
      return rules


class DummyPricePolicy(PricePolicy):
  def __init__(self, injector):
    super(DummyPricePolicy, self).__init__(injector, {})

  def floor_price(self, equity_pair, price):
    return price

  def ceil_price(self, equity_pair, price):
    return price


class PriceRule(object):
  def __init__(self, min, max, step):
    self.min = min
    self.max = max
    self.step = step
