# -*- coding: utf-8 -*-
import itertools

from carbi.utils.dyprops import DynamicProperties


def build_targets(orderbook_keys, with_okex_futures=False):
  targets = []
  for orderbook_key in orderbook_keys:
    target = OrderbookTarget()
    target.exchange = orderbook_key.split(":")[0]
    target.type = 'spot'
    target.orderbook_key = orderbook_key
    targets.append(target)
  if with_okex_futures:
    equity_pairs = ['eos/usd', 'etc/usd', 'eth/usd', 'btc/usd', 'bch/usd', 'xrp/usd', 'ltc/usd', 'btg/usd']
    contract_types = ['quarter']
    # 일단은 반드시 필요한 분기 선물만 가져오도록한다.
    # 모두 가져오려고 하면 한번에 너무 많은 요청을 동시에 날리기 떄문에 문제가 된다.
    # contract_types = ['this_week', 'next_week', 'quarter']
    for equity_pair, contract_type in itertools.product(equity_pairs, contract_types):
      target = OrderbookTarget()
      target.exchange = 'okex'
      target.type = 'future'
      target.equity_pair = equity_pair
      target.contract_type = contract_type
      targets.append(target)
    for equity_pair in equity_pairs:
      target = OrderbookTarget()
      target.exchange = 'okex'
      target.type = 'spot'
      target.orderbook_key = 'okex:{}/usdt'.format(equity_pair.split("/")[0])
      targets.append(target)
  return targets


class OrderbookTarget(DynamicProperties):
  def __str__(self):
    if self.type == 'spot':
      return "TARGET[{}]".format(self.orderbook_key)
    if self.type == 'future':
      return "TARGET[{}:f_{}_{}]".format(self.exchange, self.equity_pair, self.contract_type)
    raise NotImplementedError("INVALID ORDERBOOK_TARGET ({})".format(self.type))

  def __repr__(self):
    return self.__str__()
