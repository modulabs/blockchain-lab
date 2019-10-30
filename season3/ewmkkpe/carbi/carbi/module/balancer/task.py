# -*- coding: utf-8 -*-
import copy

from carbi.module.trade.chain import TradeChain
from carbi.module.trade.graph_builder import MultiTradeGraphBuilder


class BalancingTask(object):
  def __init__(self, chain_node, volume, rule):
    self.chain_node = chain_node
    self.volume = volume
    self.rule = rule

  def convert_to_multi_graph(self, market_ctx, balance_ctx, exchange_policies):
    assert self.volume > 0, 'volume of {} should not be zero or negative : {}'.format(self.chain_node, self.volume)

    multi_graph = _build_singluar_trade_graph(self.chain_node, self.volume, market_ctx, balance_ctx, exchange_policies)
    return multi_graph

  def __str__(self):
    return 'BalancingTask [{} : {}]'.format(self.chain_node, self.volume)

  def __repr__(self):
    return self.__str__()


def _build_singluar_trade_graph(chain_node, target_volume, market_ctx, balance_ctx, exchange_policies):
  """
  다른 TradeGraph나 MultiTradeGraph처럼 circular 형태가 아닌 단일 buy/sell만 가지고 있는 chain에 대해서
  action이 buy이면 target_equity를 target_volume만큼 사고, sell이면 target_equity를 target_volume만큼 팔 수 있는 MultiTradeGraph를 만들어 줍니다.
  단, balance_ctx나 market_ctx의 한도에 의해서 먼저 한도가 걸릴 경우 그 한도가 반영이 됩니다.
  즉, target_volume 보다 더 적게 사거나 파는 MultiTradeGraph를 만들 수도 있습니다.
  :param chain_node:
  :param target_volume:
  :param market_ctx:
  :param balance_ctx:
  :param exchange_policies:
  :return:
  """
  chain = TradeChain()
  chain.nodes = [chain_node]
  market_ctx = copy.deepcopy(market_ctx)
  balance_ctx = copy.deepcopy(balance_ctx)

  if chain_node.action == 'sell':
    # sell일 경우에는 balance_ctx에서 해당 chain_node.target_equity volume을 target_volume으로 만들어 주면 됩니다.
    asset_key = '{}:{}'.format(chain_node.exchange, chain_node.target_equity)
    org_volume = balance_ctx.assets[asset_key].volume
    balance_ctx.assets[asset_key].volume = min(target_volume, org_volume)

    multi_graph = MultiTradeGraphBuilder() \
      .with_chain(chain) \
      .with_market_ctx(market_ctx) \
      .with_balance_ctx(balance_ctx) \
      .with_exchange_policies(exchange_policies) \
      .with_profit_margin_threshold(-1) \
      .build()

    return multi_graph
  else:
    # buy인 경우에는 market_ctx에서 해당 chain_node.target_equity에 해당하는 orderbook에 걸려 있는 volume의 합이
    # 수수료를 고려하고 나서도 target_volume 이상이 되지 않도록 잘라내면 됩니다.
    orderbook_key = chain_node.orderbook_key
    assert orderbook_key in market_ctx.orderbooks
    orderbook = market_ctx.orderbooks[orderbook_key]

    # coinone 같은 경우는 buy할 경우에 실제로 받는 볼륨이 줄어들기 때문에 adjust_buy_volume을 해야 합니다.
    # fee_policy = exchange_policies.get_policy(chain_node.exchange).fee_policy
    # adjusted_volume = fee_policy.adjust_buy_volume(chain_node, target_volume)
    adjusted_volume = target_volume

    # ask쪽만 고려해서 잘라내면 됩니다.
    ask_volume_sum = 0
    truncated_asks = []
    for ask in orderbook.asks:
      if ask_volume_sum + ask['volume'] > adjusted_volume:
        new_ask = {
          'price': ask['price'],
          'volume': adjusted_volume - ask_volume_sum
        }
        truncated_asks.append(new_ask)
        break
      else:
        ask_volume_sum += ask['volume']
        truncated_asks.append(ask)

    orderbook.asks = truncated_asks

    multi_graph = MultiTradeGraphBuilder() \
      .with_chain(chain) \
      .with_market_ctx(market_ctx) \
      .with_balance_ctx(balance_ctx) \
      .with_exchange_policies(exchange_policies) \
      .with_profit_margin_threshold(-1) \
      .build()

    return multi_graph
