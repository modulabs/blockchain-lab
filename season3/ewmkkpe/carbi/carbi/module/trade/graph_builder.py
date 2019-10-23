# -*- coding: utf-8 -*-
import copy

from carbi.module.trade.graph import AssetNode, TradeGraph, MultiTradeGraph
from carbi.utils import similar, check_floor_error_value

MARKET_SELL_VOLUME_MARGIN = 0.05  # 5% margin
TOO_MANY_ITERATION_THRESHOLD = 200


def _build_asset(chain_node, input_or_output):
  is_output = input_or_output == 'output'
  equity = chain_node.output_equity(with_exchange=True) if is_output else chain_node.input_equity(with_exchange=True)
  return AssetNode(equity)


class GraphException(Exception):
  pass


class TradeGraphBuilder(object):
  def __init__(self):
    self.chain = None
    self.market_ctx = None
    self.balance_ctx = None
    self.exchange_policies = None

  def with_chain(self, chain):
    self.chain = chain
    return self

  def with_market_ctx(self, market_ctx):
    self.market_ctx = market_ctx
    return self

  def with_balance_ctx(self, balance_ctx):
    self.balance_ctx = balance_ctx
    return self

  def with_exchange_policies(self, exchange_policies):
    self.exchange_policies = exchange_policies
    return self

  def build(self):
    assets = []
    for chain_node in self.chain.nodes:
      self._build_assets(assets, chain_node)
    graph = TradeGraph(self.chain, assets)
    self._apply_qty_limit(graph)
    return graph

  def _build_assets(self, assets, chain_node):
    orderbook_key = chain_node.orderbook_key
    assert orderbook_key in self.market_ctx.orderbooks
    orderbook = self.market_ctx.orderbooks[orderbook_key]

    input_asset = _build_asset(chain_node, 'input')
    output_asset = _build_asset(chain_node, 'output')

    # 새로 만들어진 input 노드와 지금까지 연결된 노드 중 마지막 노드를 연결한다.
    # 이 때 두 노드는 같은 자산이므로 1:1 교환을 하는 것으로 생각한다.
    # 전송 수수료는 나중에 한 번에 지불되므로 고려하지 않는다.
    prev_asset = assets[-1] if len(assets) > 0 else None
    if prev_asset:
      prev_asset.add_next(input_asset, 'transfer', 1, 0)

    # 현재 chain_node가 나타내는 정보에 대한 연결을 한다.
    # 사는거면 가격 그대로 넣으면 되고 파는거면 역수를 취해서 넣는다.
    if chain_node.action == 'buy':
      ratio = 1 / orderbook.ask0_price
    else:
      ratio = orderbook.bid0_price

    # input_asset에 현재 거래에 대한 각종 수수료를 적용한다.
    fee_policy = self.exchange_policies.get_policy(chain_node.exchange).fee_policy
    ratio = fee_policy.get_effective_ratio(chain_node, ratio)
    fee = fee_policy.get_effective_fee(chain_node)

    input_asset.add_next(output_asset, chain_node.action, ratio, fee)

    assets.append(input_asset)
    assets.append(output_asset)

  def _apply_qty_limit(self, graph):
    for chain_node in graph.chain.nodes:
      trade = graph.find_trade(chain_node)
      # 모든 거래의 Input에 대해서는 내가 가지고 있는 자산 만큼만 거래를 할 수 있다.
      volume = 0
      if trade.input.equity in self.balance_ctx.assets:
        asset = self.balance_ctx.assets[trade.input.equity]
        volume = asset.volume
      trade.input.set_qty(volume)
      # 그외 호가창에 걸려있는 만큼만 사거나 팔 수 있다.
      # buy, sell에 따라서 input혹은 output에 호가창 제한을 적용해야한다.
      if trade.action == 'buy':
        volume = 0
        orderbook_key = trade.orderbook_key
        if orderbook_key in self.market_ctx.orderbooks:
          orderbook = self.market_ctx.orderbooks[orderbook_key]
          if len(orderbook.asks) > 0:
            volume = orderbook.asks[0]['volume']
        trade.output.set_qty(volume)
      elif trade.action == 'sell':
        volume = 0
        orderbook_key = trade.orderbook_key
        if orderbook_key in self.market_ctx.orderbooks:
          orderbook = self.market_ctx.orderbooks[orderbook_key]
          if len(orderbook.bids) > 0:
            volume = orderbook.bids[0]['volume']
        trade.input.set_qty(volume)


class MultiTradeGraphBuilder(object):
  def __init__(self):
    self.chain = None
    self.market_ctx = None
    self.balance_ctx = None
    self.exchange_policies = None
    self.profit_margin_threshold = 0.0 / 100.0

  def with_chain(self, chain):
    self.chain = chain
    return self

  def with_market_ctx(self, market_ctx):
    self.market_ctx = copy.deepcopy(market_ctx)
    return self

  def with_balance_ctx(self, balance_ctx):
    self.balance_ctx = copy.deepcopy(balance_ctx)
    return self

  def with_exchange_policies(self, exchange_policies):
    self.exchange_policies = exchange_policies
    return self

  def with_profit_margin_threshold(self, profit_margin_threshold):
    self.profit_margin_threshold = profit_margin_threshold
    return self

  def build(self):
    self.balance_ctx = self._apply_market_sell_volume_margin(self.balance_ctx, self.chain)
    self.profit_margin_threshold = self._adjust_profit_margin_threshold_if_binance(self.profit_margin_threshold, self.chain)

    multi_trade_graph = MultiTradeGraph(self.chain)

    # 만약 multi_trade_graph를 만들기 위해 market_ctx, balance_ctx에
    # 필요한 orderbook과 asset가 들어가 있지 않으면 바로 포기한다.
    if not self._check_ctx_requirements(self.chain):
      return multi_trade_graph

    while_count = 0
    while True:
      graph = TradeGraphBuilder() \
        .with_chain(self.chain) \
        .with_market_ctx(self.market_ctx) \
        .with_balance_ctx(self.balance_ctx) \
        .with_exchange_policies(self.exchange_policies) \
        .build()

      # 현재 그래프를 사용할 수 있는지 확인한다.
      # 어차피 다음에 만들어지는 그래프일수록 더 불리한 그래프이므로
      # 현재 만들어진 그래프가 불리한 그래프면 그냥 여기서 끝내버린다.
      insufficient_volume = graph.trading_volume <= 0
      insufficient_margin = graph.profit_margin < self.profit_margin_threshold
      if insufficient_volume or insufficient_margin:
        break

      # 이번 트레이드 그래프는 최소 조건을 충족 시켰으므로,
      # 이번 트레이드 그래프를 멀티 트레이드 그래프에 추가합니다.
      multi_trade_graph.add_trade_graph(graph)

      # 다음 트레이드 그래프를 만들기 위해서는
      # 이번 트레이드 그래프로 소모된 자산을 호가창과 자산에 반영해야 합니다.
      self._apply_consumed_qty(graph)

      # 소모된 자산을 호가창과 자산에 반영한 후 남아있는 자산이 있는지 확인한다.
      # 만약 다음 TradeGraph를 계산할 수 있을 만큼 자산이 없으면 그먄 둔다.
      insufficient_balance = not self._is_trade_volume_available(graph)
      if insufficient_balance:
        break

      # 그래프를 만들기 위해 while문을 너무 많이 돌면 실패로 처리한다.
      if while_count > TOO_MANY_ITERATION_THRESHOLD:
        raise GraphException('TOO_MANY_ITERATION_THRESHOLD: Error occurs during building multi_trade_graph.')

      while_count += 1

    # 거래소에서 거래 가능하도록 floor한 경우 거래해야하는 값과 너무 차이가 나는 경우를 체크합니다.
    # 보통은 값이 거래하는 값이 너무 작은 경우 이므로 이런 경우는 에러로 처리해도 상관 없습니다.
    self._check_floored_qty_or_throw(multi_trade_graph)

    # 거래소에서 거래 가능하도록 floor해서 차이나는 거래량만큼 그래프에 반영합니다.
    # floor때문에 생기는 오차때문에 의도하는 수량을 사거나 팔게 되는 에러를 최소화 하기 위함입니다.
    self._apply_floor_diff_or_throw(multi_trade_graph)

    # 모든 조건이 충족된 multi_trade_graph만 리턴합니다.
    return multi_trade_graph

  def _apply_market_sell_volume_margin(self, balance_ctx, chain):
    """
    limit 주문을 통해서 market을 대신하는 거래소에서는, 꼭 마켓 주문으로 처리가 될 수 있도록 다소 높거나 낮은 가격으로 던지게 되는데,
    이 때 base equity의 잔고가 부족한 경우 잔고 부족 에러로 주문이 들어가지 않을 위험이 있다.
    이럴 경우를 막기 위해서 약간 여유를 두고 거래해야 한다.
    """
    base_asset_keys = set()
    for node in chain.nodes:
      if node.action == 'buy':
        # base_equity 입장에서는 buy일 때만 자신의 volume이 줄어들기 때문에 이 경우에만 조정하면 됩니다.
        base_asset_keys.add('%s:%s' % (node.exchange, node.base_equity))

    assets = balance_ctx.assets
    for asset in assets.values():
      key = asset.key
      if key in base_asset_keys:
        asset.volume *= 1 - MARKET_SELL_VOLUME_MARGIN
    return balance_ctx

  def _adjust_profit_margin_threshold_if_binance(self, profit_margin_threshold, chain):
    # XXX(Andrew): 임시코드, chain에 들어 있는 binance asset의 개수에 따라서 profit_margin_threshold를 taker_fee 만큼 올려줍니다.
    binance_fee_policy = self.exchange_policies.get_policy('binance').fee_policy

    if binance_fee_policy.bnb_fee_deduct_enabled():
      binance_taker_fee = binance_fee_policy._get_taker_fee()
      binance_node_count = 0
      for node in chain.nodes:
        if node.exchange == 'binance':
          binance_node_count += 1

      return profit_margin_threshold + binance_taker_fee * binance_node_count
    else:
      return profit_margin_threshold

  def _check_ctx_requirements(self, chain):
    """
    그래프를 만들기 위해 market_ctx와 balance_ctx에 orderbook과 asset이 제대로 들어가 있어야한다.
    """
    for chain_node in chain.nodes:
      orderbook_key = chain_node.orderbook_key
      if orderbook_key not in self.market_ctx.orderbooks:
        return False
      input_equity = chain_node.input_equity(with_exchange=True)
      if input_equity not in self.balance_ctx.assets:
        return False
      output_equity = chain_node.output_equity(with_exchange=True)
      if output_equity not in self.balance_ctx.assets:
        return False
    return True

  def _apply_consumed_qty(self, graph):
    """
    주어진 TradeGraph로 인해 소모되는 자산과 호가 물량을 반영한다.
    """
    for chain_node in graph.chain.nodes:
      trade = graph.find_trade(chain_node)

      # Trade가 실행되면 Input에 대한 보유 값이 소모 된다.
      # KRW로 BTC를 사면 가지고 있던 KRW가 사용되고 ETH를 팔면 가지고 있던 ETH가 사용된다.
      assert trade.input.equity in self.balance_ctx.assets
      asset = self.balance_ctx.assets[trade.input.equity]
      asset.volume -= trade.input.qty

      # Trade가 실행되면서 Orderbook의 호가를 밀고 올라간다.
      # Buy인 경우 Output만큼 호가에서 지워줘야 한다.
      # KRW로 BTC를 산 경우 BTC만크 호가에서 지워야 한다.
      # Sell인 경우 Input만큼 호카에서 지워줘야 한다.
      # ETH를 팔아 KRW를 얻는 경우 ETH만큼 호가에서 지워야 한다.
      orderbook_key = trade.orderbook_key
      assert orderbook_key in self.market_ctx.orderbooks
      orderbook = self.market_ctx.orderbooks[orderbook_key]
      if trade.action == 'buy':
        volume = orderbook.asks[0]['volume']
        qty = trade.output.qty
        if similar(volume, qty):
          del orderbook.asks[0]
        else:
          orderbook.asks[0]['volume'] -= qty
      elif trade.action == 'sell':
        volume = orderbook.bids[0]['volume']
        qty = trade.input.qty
        if similar(volume, qty):
          del orderbook.bids[0]
        else:
          orderbook.bids[0]['volume'] -= qty

  def _is_trade_volume_available(self, graph):
    """
    주어진 TradeGraph에서 일어나는 거래를 하는데 필요한 자산이나 호가 물량이 남아있는지 확인한다.
    """
    for chain_node in graph.chain.nodes:
      trade = graph.find_trade(chain_node)

      # 내 계좌에 거래에 필요한 자산이 있으면 volume을 가져온다.
      volume = 0
      if trade.input.equity in self.balance_ctx.assets:
        asset = self.balance_ctx.assets[trade.input.equity]
        volume = asset.volume
      if volume <= 0:
        return False

      # 호가창에 거래할 수 있는 물량이 남아 있는지 확인한다.
      # 호가창을 완전히 밀고 올라가 아무 호가도 남아있지 않으면 거래가 불가능하다.
      orderbook_key = trade.orderbook_key
      assert orderbook_key in self.market_ctx.orderbooks
      orderbook = self.market_ctx.orderbooks[orderbook_key]
      if trade.action == 'buy':
        if len(orderbook.asks) == 0:
          return False
      elif trade.action == 'sell':
        if len(orderbook.bids) == 0:
          return False
    return True

  def _check_floored_qty_or_throw(self, multi_graph):
    """
    거래소에 따라 거래하려는 가상화폐의 qty를 floor를 한 후 거래를 해야합니다.
    원래 거래해야하는 값과 floor한 값의 차이가 너무 많이나면 의도한대로 거래가 되지 않게 됩니다.
    이런 경우는 Exception을 던져서 거래가 일어나지 않도록 해야합니다.
    """
    for chain_node in multi_graph.chain.nodes:
      exchange = chain_node.exchange
      volume_policy = self.exchange_policies.get_policy(exchange).volume_policy

      equity_pair = chain_node.equity_pair
      if chain_node.action == 'buy':
        buy_qty = multi_graph.total_output_qty(chain_node)
        floored_buy_qty = volume_policy.floor_volume(equity_pair, buy_qty)
        if not check_floor_error_value(buy_qty, floored_buy_qty):
          error_msg = 'ROUND_ERROR: %s floor_volume(%s) != %s' % (chain_node, buy_qty, floored_buy_qty)
          raise GraphException(error_msg)
      elif chain_node.action == 'sell':
        sell_qty = multi_graph.total_input_qty(chain_node)
        floored_sell_qty = volume_policy.floor_volume(equity_pair, sell_qty)
        if not check_floor_error_value(sell_qty, floored_sell_qty):
          error_msg = 'ROUND_ERROR: %s floor_volume(%s) != %s' % (chain_node, sell_qty, floored_sell_qty)
          raise GraphException(error_msg)

  def _apply_floor_diff_or_throw(self, multi_graph):
    """
    거래소에 따라 거래하려는 가상화폐의 qty를 floor를 한 후 거래를 해야합니다.
    원래 거래해야하는 값과 floor한 값의 차이가 너무 많이나면 의도한대로 거래가 되지 않게 됩니다.
    따라서 floor한 값을 그래프에 반영해줍니다.
    """
    # 원래는 여러 트레이드 중에서 가장 차이가 많이 나는 트레이드를 기준으로 diff를 계산해야합니다.
    # 그러나 우리가 돌리는 트레이드는 보통 coinone부터 buy 거래를 시작하고
    # 보통은 coinone의 소수점이 가장 낮으므로 처음 buy를 기준으로 합니다.
    # 나중에는 고쳐져야 할 것 같습니다.
    buying_nodes = filter(lambda n: n.action == 'buy', multi_graph.chain.nodes)
    if len(buying_nodes) == 0:
      return
    first_buying_node = buying_nodes[0]

    exchange = first_buying_node.exchange
    equity_pair = first_buying_node.equity_pair
    volume_policy = self.exchange_policies.get_policy(exchange).volume_policy

    trade_qty = multi_graph.total_output_qty(first_buying_node)
    floored_trade_qty = volume_policy.floor_volume(equity_pair, trade_qty)

    # 이 수치만큼 기존 multi_trade_graphs.graphs에서 빼줘야 합니다.
    diff = trade_qty - floored_trade_qty

    while_count = 0
    while diff > 0:
      graph = multi_graph.graphs.pop()
      trade = graph.find_trade(first_buying_node)
      qty = trade.qty
      if qty <= diff:
        # qty가 diff보다 작으면 이 그래프는 배제시킨다.
        diff -= qty
      else:
        # qty가 diff보다 크면 이 트레이드의 qty를 diff 줄이고 다시 넣어준다.
        # 그리고 diff를 multi_graph에 모두 반영했으므로 break로 나가고 끝낸다.
        trade.output.set_qty(qty - diff)
        multi_graph.add_trade_graph(graph)
        break

      # 너무 많이 돌면 실패 처리 한다.
      if while_count > TOO_MANY_ITERATION_THRESHOLD:
        raise GraphException(
          'TOO_MANY_ITERATION_THRESHOLD: Error occurs during applying floor diff to multi_trade_graph.')
      while_count += 1
