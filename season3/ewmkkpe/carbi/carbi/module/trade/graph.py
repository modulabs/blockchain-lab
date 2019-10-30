# -*- coding: utf-8 -*-
import sys


class TradeEdge(object):
  def __init__(self, input, output, action, ratio, fee):
    """
    TradeEdge 정보를 만들어낸다.
    :param base: 해당 거래의 base가 되는 AssetNode 객체가 들어온다. (input)
    :param target: 해당 거래의 target이 되는 AssetNode 객체가 들어온다. (output)
    :param action: 이 거래의 action이 들어온다. (buy, sell, transfer)
    :param ratio: 이 거래의 ratio가 들어온다. (buy:price, sell:1/price, trsnfer:1)
    :param fee: 이 거래의 수수료에 대한 정보가 들어온다.
    """
    # input.qty * ratio * (1-fee) => output.qty
    # output.qty / ratio / (1-fee) => input.qty
    self.input = input
    self.output = output
    self.action = action
    self.ratio = ratio
    self.fee = fee

  @property
  def orderbook_key(self):
    # action이 transfer인 경우에 대한 처리는 제대로 안되어 있음.
    input_exchange, input_equity = self.input.equity.split(':')
    output_exchange, output_equity = self.output.equity.split(':')
    if self.action == 'buy':
      return '%s:%s/%s' % (input_exchange, output_equity, input_equity)
    else:
      return '%s:%s/%s' % (input_exchange, input_equity, output_equity)

  @property
  def price(self):
    """
    ratio는 거래에서의 교환 비율이다.
    price는 실제 orderbook에 찍히는 가격이다.
    """
    if self.action == 'buy':
      return 1 / self.ratio
    else:
      return self.ratio

  @property
  def qty(self):
    """
    거래가 일어날때 실제 base 기준으로 얼마 어치를 사거나 파는지
    """
    if self.action == 'buy':
      return self.input.qty
    else:
      return self.output.qty

  def calculate_output_qty(self, input_qty):
    return input_qty * self.ratio * (1 - self.fee)

  def calculate_input_qty(self, output_qty):
    return output_qty / self.ratio / (1 - self.fee)


class AssetNode(object):
  def __init__(self, equity):
    """
    AssetNode 객체를 만들어낸다.
    :param equity:거래소 정보까지 달린 equity symbol이 들어온다. (upbit:krw, cex:btc)
    """
    self.equity = equity
    self.qty = sys.maxint
    self.next_trade = None
    self.prev_trade = None

  def add_next(self, target_asset, action, ratio, fee):
    trade = TradeEdge(self, target_asset, action, ratio, fee)
    self.next_trade = trade
    target_asset.prev_trade = trade
    return trade

  def set_qty(self, qty, sender=None):
    if qty < self.qty:
      self.qty = qty
      if self.next_trade is not None:
        if sender is None or sender is not self.next_trade.output:
          next_qty = self.next_trade.calculate_output_qty(qty)
          self.next_trade.output.set_qty(next_qty, sender=self)
      if self.prev_trade is not None:
        if sender is None or sender is not self.prev_trade.input:
          prev_qty = self.prev_trade.calculate_input_qty(qty)
          self.prev_trade.input.set_qty(prev_qty, sender=self)


class TradeGraph(object):
  def __init__(self, chain, assets):
    self.chain = chain
    self.assets = assets
    self.trades = self._build_trades()

  def _build_trades(self):
    trades = []
    for asset in self.assets:
      if asset.next_trade:
        trades.append(asset.next_trade)
    return trades

  def find_trade(self, chain_node):
    """
    TradeGraph에서 chain_node에 해당하는 TradeEdge 객체를 가져온다.
    하나의 TradeGraph에서 같은 Orderbook을 바라보는건 애초에 수수료 낭비이므로 그런 일은 없다고 가정했다.
    이 함수를 이용해 TradeEdge를 LookUp한다.
    """
    trades = filter(lambda x: x.orderbook_key == chain_node.orderbook_key, self.trades)
    assert len(trades) == 1
    return trades[0]

  @property
  def profit(self):
    # In terms of initiating asset
    return self.assets[-1].qty - self.assets[0].qty

  @property
  def trading_volume(self):
    # In terms of initiating asset
    return self.assets[0].qty

  @property
  def profit_margin(self):
    if self.trading_volume > 0:
      return self.profit / self.trading_volume
    else:
      return 0

  def equity_changes(self, equity):
    """
    이 그래프의 트레이드가 실행됨으로 인해 변화되는 equity의 qty를 계산한다.
    어떤 거래에 의해 coinone:krw가 소모되기도 하고 늘어나기도 하는데 그 합을 계산한다.
    """
    changes = 0
    index = 0
    for asset in self.assets:
      if asset.equity == equity:
        if index % 2 == 0:
          # index가 짝수면 input_asset입니다.
          changes -= asset.qty
        else:
          # index가 홀수면, output_asset입니다.
          changes += asset.qty
      index += 1
    return changes

  def equity_trading_volume(self, equity):
    """
    이 그래프의 트레이드가 실행됨으로 특정 equity의 거래 규모의 평균을 계산한다.
    어떤 거래에 의해 coinone:krw가 소모되기도 하고 늘어나기도 하는데 그 규모의 평균을 계산한다.
    """
    count = 0
    trading_volume = 0
    for asset in self.assets:
      if asset.equity == equity:
        trading_volume += abs(asset.qty)
        count += 1

    if count == 0:
      return 0
    return trading_volume / count

  def __str__(self):
    str_builder = ''
    for chain_node in self.chain.nodes:
      trade = self.find_trade(chain_node)
      input_qty = trade.input.qty
      output_qty = trade.output.qty
      price = trade.price
      str_builder += '  %s: %s(-%.5f)->%s(+%.5f) [x:%s]\n' % \
                     (chain_node,
                      chain_node.input_equity(),
                      input_qty,
                      chain_node.output_equity(),
                      output_qty,
                      price)
    return 'TradeGraph(\n%s)' % str_builder

  def __repr__(self):
    return self.__str__()


class MultiTradeGraph(object):
  def __init__(self, chain):
    self.chain = chain
    # 앞쪽이 더 유리한 가격, 뒤쪽이 더 불리한 가격입니다.
    self.graphs = []

  def add_trade_graph(self, trade_graph):
    self.graphs.append(trade_graph)

  def total_input_qty(self, chain_node):
    qty = 0
    for graph in self.graphs:
      trade = graph.find_trade(chain_node)
      qty += trade.input.qty
    return qty

  def total_output_qty(self, chain_node):
    qty = 0
    for graph in self.graphs:
      trade = graph.find_trade(chain_node)
      qty += trade.output.qty
    return qty

  def avg_price(self, chain_node):
    total_qty = 0
    total_price_qty = 0
    for graph in self.graphs:
      trade = graph.find_trade(chain_node)
      total_qty += trade.qty
      total_price_qty += trade.qty * trade.price
    if total_qty == 0:
      return 0
    else:
      return total_price_qty / total_qty

  def total_profit(self):
    # In terms of initiating asset
    profit = 0
    for graph in self.graphs:
      profit += graph.profit
    return profit

  def total_trading_volume(self):
    # In terms of initiating asset
    volume = 0
    for graph in self.graphs:
      volume += graph.trading_volume
    return volume

  def total_profit_margin(self):
    if self.total_trading_volume() > 0:
      return self.total_profit() / self.total_trading_volume()
    return 0

  def total_equity_changes(self, equity):
    volume = 0
    for graph in self.graphs:
      volume += graph.equity_changes(equity)
    return volume

  def total_equity_trading_volume(self, equity):
    volume = 0
    for graph in self.graphs:
      volume += graph.equity_trading_volume(equity)
    return volume

  def __str__(self):
    str_builder = ''
    for chain_node in self.chain.nodes:
      input_qty = self.total_input_qty(chain_node)
      output_qty = self.total_output_qty(chain_node)
      price = self.avg_price(chain_node)
      str_builder += '  %s: %s(-%.5f)->%s(+%.5f) [x:%s]\n' % \
                     (chain_node,
                      chain_node.input_equity(),
                      input_qty,
                      chain_node.output_equity(),
                      output_qty,
                      price)
    return 'MultiTradeGraph[graph:%s](\n%s)' % (len(self.graphs), str_builder)

  def __repr__(self):
    return self.__str__()
