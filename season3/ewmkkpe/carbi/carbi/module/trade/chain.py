# -*- coding: utf-8 -*-


def get_orderbook_keys(chains):
  """
  주어진 TradeChain리스트와 연관된 모든 orderbook_key 리스트를 가져온다.
  """
  orderbook_keys = set()
  for chain in chains:
    for node in chain.nodes:
      # inspector에서 김프 체크할때는 외환시장에 대한 정보가 chain에 들어가 있다.
      # 이런 경우는 orderbook에서는 제외시켜줘야한다.
      if node.exchange == 'currency':
        continue
      orderbook_keys.add(node.orderbook_key)
  return list(orderbook_keys)


class TradeChain(object):
  __slots__ = (
    'nodes',
  )

  @staticmethod
  def from_string(c):
    # 아래와 같은 형태의 문자열을 잘라서 Chain 객체로 만들어낸다.
    # ask(upbit:btc/krw),ask(upbit:eth/btc),bid(upbit:eth/krw)
    chain = TradeChain()
    chain.nodes = []
    entries = c.split(',')
    for entry in entries:
      (action, market) = entry.replace(')', '').split('(')
      (exchange, equity_pair) = market.split(':')
      (target_equity, base_equity) = equity_pair.split('/')

      chain_node = TradeChainNode()
      chain_node.exchange = exchange
      chain_node.target_equity = target_equity
      chain_node.base_equity = base_equity
      chain_node.action = action
      chain.nodes.append(chain_node)
    assert chain._validate(), 'Invalid chain: %s' % c
    return chain

  def _validate(self):
    try:
      nodes = self.nodes
      assert len(nodes) > 0
      # 체인이 시작될때 소모되는 Equity와 마지막 나오는 Equity가 동일해야한다.
      # 이를 같이 로직에서 처리하기 위해 for문이 시작되기 전에 마지막 output_equity로 설정해준다.
      prev_output_equity = nodes[len(nodes) - 1].output_equity()
      for node in nodes:
        # 모든 노드의 action이 제대로된 값인지 확인한다.
        assert node.action in ['buy', 'sell']
        # 각 노드들의 Equity가 제대로 연결되어 있는지 확인한다.
        # 만약 prev_output_equity가 설정되어있지 않다
        assert prev_output_equity == node.input_equity()
        prev_output_equity = node.output_equity()
      return True
    except AssertionError:
      return False

  def participating_equities(self, with_exchange=False):
    participating_equities = set()
    for node in self.nodes:
      [participating_equities.add(e) for e in node.participating_equities(with_exchange=with_exchange)]
    return list(participating_equities)

  @property
  def contains_binance_exchange(self):
    for node in self.nodes:
      if node.is_binance_exchange:
        return True
    return False

  @property
  def first_base_equity(self):
    return self.nodes[0].base_equity

  def __str__(self):
    return ','.join(['{}'.format(node) for node in self.nodes])

  def __repr__(self):
    return self.__str__()


class TradeChainNode(object):
  __slots__ = (
    'exchange',
    'target_equity',
    'base_equity',
    'action',
  )

  @property
  def orderbook_key(self):
    """
    이 거래가 일어나는 Orderbook에 대한 정보를 가져온다.
    """
    return '%s:%s/%s' % (self.exchange, self.target_equity, self.base_equity)

  @property
  def equity_pair(self):
    """
    이 거래에 대한 equity pair를 가져온다.
    """
    return '%s/%s' % (self.target_equity, self.base_equity)

  def input_equity(self, with_exchange=False):
    """
    이 거래를 하게 될 때 사용되는 Equity를 가져온다.
    buy(conineone:btc/krw): krw
    sell(upbit:eth/btc): eth
    :return: 거래를 할 때 사용 되는 Equity
    """
    equity = self.base_equity if self.action == 'buy' else self.target_equity
    if with_exchange:
      equity = '%s:%s' % (self.exchange, equity)
    return equity

  def output_equity(self, with_exchange=False):
    """
    이 거래를 하게 될 때 얻게 되는 Equity를 가져온다.
    buy(coinone:btc/krw): btc
    sell(upbit:eth/btc): btc
    :return: 거래를 할 때 얻게 되는 Equity
    """
    equity = self.base_equity if self.action == 'sell' else self.target_equity
    if with_exchange:
      equity = '%s:%s' % (self.exchange, equity)
    return equity

  def participating_equities(self, with_exchange=False):
    """
    이 거래에 참여하는 equity를 가져온다.
    Graph에서 참여하는 모든 equity 리스트를 가져올때 필요하다.
    buy(coinone:btc/krw): btc, krw
    sell(upbit:eth/btc): eth, btc
    """
    return [
      self.input_equity(with_exchange=with_exchange),
      self.output_equity(with_exchange=with_exchange),
    ]

  @property
  def is_binance_exchange(self):
    return self.exchange == 'binance'

  def __str__(self):
    return "%s(%s:%s/%s)" % (self.action, self.exchange, self.target_equity, self.base_equity)

  def __repr__(self):
    return self.__str__()

  def __eq__(self, other):
    if type(other) is not TradeChainNode:
      return False

    return self.exchange == other.exchange and self.base_equity == other.base_equity \
           and self.target_equity == other.target_equity and self.action == other.action

  def __ne__(self, other):
    return not self.__eq__(other)


class Chains(object):
  def __init__(self):
    pass

  @staticmethod
  def load_from_file(file):
    chains = []
    with open(file, "rU") as f:
      for line in f:
        line = line.strip()
        if line.startswith('#'):
          continue
        if len(line) == 0:
          continue
        chains.append(TradeChain.from_string(line))
    return chains
