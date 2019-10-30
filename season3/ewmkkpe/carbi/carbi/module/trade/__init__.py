# -*- coding: utf-8 -*-
import sys

from carbi.config import CarbiConfigKeys
from carbi.module.trade.bundle import TradeTaskBundle, TradeTask
from carbi.module.trade.graph import TradeGraph, MultiTradeGraph
from carbi.module.trade.graph_builder import MultiTradeGraphBuilder

MARKET_PRICE_MARGIN = 0.04  # market price는 언제나 4% 정도 더 싸거나 비싸게 부릅니다.


class ProfitSeeker(object):
  def __init__(self, injector):
    self.injector = injector
    self.logger = injector.logger
    self.profit_margin_threshold = injector.config[CarbiConfigKeys.PROFIT_MARGIN_THRESHOLD]

  def find_profitable_trade_bundles(self, chains, market_ctx, balance_ctx):
    bundles = []
    for chain in chains:
      multi_graph = self._build_trade_graph(chain, market_ctx, balance_ctx)
      if not multi_graph:
        continue
      if multi_graph.total_profit() <= 0:
        continue
      bundle = TradeTaskBundle(self.injector, market_ctx, multi_graph)
      bundle.tasks = self._build_trade_tasks(multi_graph)
      bundles.append(bundle)
    return bundles

  def _build_trade_graph(self, chain, market_ctx, balance_ctx):
    # 이번 그래프를 만드는데 실패했다고 다른 그래프를 만드는 것을 포기하면 안되므로,
    # 그래프를 만들다가 실패하면 None을 리턴한다.
    try:
      exchange_policies = self.injector.exchange_policies
      multi_graph = MultiTradeGraphBuilder() \
        .with_chain(chain) \
        .with_market_ctx(market_ctx) \
        .with_balance_ctx(balance_ctx) \
        .with_exchange_policies(exchange_policies) \
        .with_profit_margin_threshold(self.profit_margin_threshold) \
        .build()
      return multi_graph
    except Exception as e:
      self._handle_exception(e)
      return None
    except AssertionError as e:
      self._handle_exception(e)
      return None

  def _build_trade_tasks(self, multi_graph):
    tasks = []
    for chain_node in multi_graph.chain.nodes:
      trade = multi_graph.graphs[-1].find_trade(chain_node)
      task = TradeTask(chain_node)
      exchange = chain_node.exchange
      equity_pair = chain_node.equity_pair
      exchange_policy = self.injector.exchange_policies.get_policy(exchange)

      if chain_node.action == 'buy':
        # 가장 불리한 graph의 buy 이니까 더 비싸게 ...
        price = trade.price * (1 + MARKET_PRICE_MARGIN)
        volume = multi_graph.total_output_qty(chain_node)
        order_volume = exchange_policy.fee_policy.adjust_buy_volume(chain_node, volume)
        # 거래소의 정책에 맞게 price과 volume값을 약간 조절해야한다.
        task.price = exchange_policy.price_policy.ceil_price(equity_pair, price)
        task.volume = exchange_policy.volume_policy.floor_volume(equity_pair, order_volume)
      else:
        # 가장 불리한 graph의 sell 이니까 더 싸게 ...
        price = trade.price * (1 - MARKET_PRICE_MARGIN)
        order_volume = multi_graph.total_input_qty(chain_node)
        # 거래소의 정책에 맞게 price과 volume값을 약간 조절해야한다.
        task.price = exchange_policy.price_policy.floor_price(equity_pair, price)
        task.volume = exchange_policy.volume_policy.floor_volume(equity_pair, order_volume)
      tasks.append(task)
    return tasks

  def _handle_exception(self, e):
    # Round error에 대한 에러만 무시하고 나머지는 raise한다.
    if 'ROUND_ERROR' in e.message:
      return
    self.logger.error(e, exc_info=sys.exc_info())
