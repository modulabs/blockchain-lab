# -*- coding: utf-8 -*-
class FeePolicy(object):
  def __init__(self, config):
    self.config = config

  def get_effective_ratio(self, chain_node, ratio):
    raise NotImplementedError()

  def get_effective_fee(self, chain_node):
    raise NotImplementedError()

  def adjust_buy_volue(self, chain_node, volume):
    raise NotImplementedError()

  def bnb_fee_deduct_enabled(self):
    return False


def _build_fee_policies(config):
  # to avoid circular reference
  from carbi.policy.fee import cex, coinone, bitfinex, korbit, binance
  fee_policies = dict()
  fee_policies['cex'] = cex.CexFeePolicy(config)
  fee_policies['coinone'] = coinone.CoinoneFeePolicy(config)
  fee_policies['bitfinex'] = bitfinex.BitfinexFeePolicy(config)
  fee_policies['korbit'] = korbit.KorbitFeePolicy(config)
  fee_policies['binance'] = binance.BinanceFeePolicy(config)
  return fee_policies


class FeePolicyProvider(object):
  def __init__(self, config):
    self.fee_policies = _build_fee_policies(config)

  def get_policy(self, exchange):
    assert exchange in self.fee_policies
    return self.fee_policies[exchange]

