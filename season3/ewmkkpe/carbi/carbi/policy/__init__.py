# -*- coding: utf-8 -*-
from carbi.policy.price import PricePolicyProvider
from carbi.policy.volume import VolumePolicyProvider
from carbi.policy.fee import FeePolicyProvider


def _build_exchange_policies(config):
  exchanges = ['coinone', 'cex', 'bitfinex', 'korbit', 'binance']
  exchange_policies = dict()

  fee_provider = FeePolicyProvider(config)
  price_provider = PricePolicyProvider(config)
  volume_provider = VolumePolicyProvider(config)

  for exchange in exchanges:
    fee_policy = fee_provider.get_policy(exchange)
    price_policy = price_provider.get_policy(exchange)
    volume_policy = volume_provider.get_policy(exchange)

    exchange_policy = ExchangePolicy(fee_policy, price_policy, volume_policy)
    exchange_policies[exchange] = exchange_policy
  return exchange_policies


class ExchangePolicyProvider(object):
  def __init__(self, config):
    self.exchange_policies = _build_exchange_policies(config)

  def get_policy(self, exchange):
    assert exchange in self.exchange_policies
    return self.exchange_policies[exchange]


class ExchangePolicy(object):
  def __init__(self, fee_policy, price_policy, volume_policy):
    self.fee_policy = fee_policy
    self.price_policy = price_policy
    self.volume_policy = volume_policy
