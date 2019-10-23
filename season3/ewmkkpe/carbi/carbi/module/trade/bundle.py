# -*- coding: utf-8 -*-
import copy
import sys

import gevent
from gevent.event import AsyncResult

from carbi.cmp import to_comparable_repr
from carbi.const import CURRENCY_SYMBOLS
from carbi.module.trade.executor import TradeExecutorFactory
from carbi.module.trade.scheduler import schedule_tasks
from carbi.utils import similar, geographical_interpolate

BACKOFF_STEPS = [0, 1, 2, 3, 5]


class TradeTaskStatus(object):
  READY = 'ready'
  PENDING = 'pending'
  SUCCESS = 'success'
  ERROR = 'error'

  def __init__(self):
    pass


class TradeTask(object):
  def __init__(self, chain_node):
    assert chain_node.action in ['buy', 'sell']
    self.chain_node = chain_node
    self.status = TradeTaskStatus.READY
    self.price = None
    self.volume = None
    self.error = None

  def pending(self):
    self.status = TradeTaskStatus.PENDING
    return self

  def participating_equities(self):
    return self.chain_node.participating_equities(with_exchange=True)

  def __str__(self):
    return 'Task({} {} @ {} [{}])'.format(self.chain_node, self.volume, self.price, self.status)

  def __repr__(self):
    return self.__str__()


class TradeTaskBundle(object):
  def __init__(self, injector, market_ctx, multi_graph):
    self.injector = injector
    self.logger = injector.logger
    self.market_ctx = market_ctx
    self.executor_factory = TradeExecutorFactory(injector)
    self.graph = multi_graph
    self.tasks = []
    self.before_balance = None
    self.after_balance = None

  @property
  def is_satisfy_profit_threshold(self):
    # 거래량이 너무 작아 한번에 얻을 수 있는 이득이 천원/1달러 이하인 경우 무시한다.
    first_base_equity = self.graph.chain.first_base_equity

    if first_base_equity == 'krw':
      return self.graph.total_profit() > 1000.0
    elif first_base_equity in ['usd' or 'usdt']:
      return self.graph.total_profit() > 1.0
    else:
      # base가 fiat이 아닌 단위로 잘못오면 print 합니다.
      self.logger.warn("Can't recognize base equity : {}, this is not registered fiat currency.".format(first_base_equity))
      return False

  def execute(self, balance_tracker):
    self.logger.info('EXECUTE_TRADE: {}'.format(self.graph))
    self.logger.info('TASKS:\n{}'.format('\n'.join(['  {}'.format(task) for task in self.tasks])))
    executions = []
    grouped_tasks = schedule_tasks(self.tasks)
    for group_key, tasks in grouped_tasks.iteritems():
      exchange = group_key.split(".")[0]
      executor = self.executor_factory.get_executor(exchange)
      async_result = AsyncResult()
      execution = gevent.spawn(self._execute_trade_tasks, async_result, executor, tasks)
      executions.append(execution)

    # 모든 실행한 트레이드가 끝날때까지 기다린다.
    # TODO: Task가 실패하면 FailOver를 해야할 수도 있다.
    gevent.joinall(executions)

    correct = self._try_update_and_get_balance(balance_tracker)
    result = TradeTaskBundleExecutionResult(self.market_ctx, self.graph, self.tasks)
    result.before_balance = self.before_balance
    result.after_balance = self.after_balance
    result.is_balance_updated_correctly = correct
    return result

  def _execute_trade_tasks(self, async_result, executor, tasks):
    # 혹시라도 buy할때 KRW/USD가 모자른 경우를 방지하기 위해 sell부터 실행하고 나중에 buy를 실행한다.
    sorted_tasks = sorted(tasks, key=lambda x: x.chain_node.action, reverse=True)
    sorted_tasks = map(lambda x: x.pending(), sorted_tasks)
    all_tasks_succeed = True
    for task in sorted_tasks:
      chain_node = task.chain_node
      equity_pair = chain_node.equity_pair
      price = task.price
      volume = task.volume
      try:
        if chain_node.action == 'sell':
          executor.sell(equity_pair=equity_pair, price=price, volume=volume)
        else:
          executor.buy(equity_pair=equity_pair, price=price, volume=volume)
        task.status = TradeTaskStatus.SUCCESS
      except Exception as e:
        self.logger.error(e, exc_info=sys.exc_info())
        all_tasks_succeed = False
        task.status = TradeTaskStatus.ERROR
        task.error = e
        break
    # 모든 결과가 성공했을때만 True를 리턴한다.
    async_result.set(all_tasks_succeed)

  def _try_update_and_get_balance(self, balance_tracker):
    before_balance = copy.deepcopy(balance_tracker.get())
    after_balance = copy.deepcopy(balance_tracker.get())

    participating_equities = self.participating_equities

    # 현재 거래와 관련해서 자산의 변경이 제대로 되었는지 체크한다.
    is_correct = False
    retry_count = 0
    while retry_count < 5:
      sleep_millis = BACKOFF_STEPS[retry_count]
      gevent.sleep(sleep_millis)

      balance_tracker.update()
      after_balance = copy.deepcopy(balance_tracker.get())

      # 각 자산의 차이를 가져온다.
      equity_changes = {}
      for equity in participating_equities:
        new_volume = after_balance.assets[equity].volume
        old_volume = before_balance.assets[equity].volume
        volume_change = new_volume - old_volume
        equity_changes[equity] = volume_change

      # 이번 트레이드에 의해 자산의 변화가 제대로 반영되었는지 체크한다.
      crypto_margin_of_error = 0.01  # 1 %
      is_correct = True
      for equity in participating_equities:
        actual_changes = equity_changes[equity]
        expected_changes = self.graph.total_equity_changes(equity)
        symbol = equity.split(':')[1]
        if symbol in CURRENCY_SYMBOLS:
          # fiat currency의 경우 거래 규모에 따라 의도한 값과 비례해서 오차가 생길 수 있다.
          trading_volume = self.graph.total_equity_trading_volume(equity)

          # 기하평균인데 좀 더 expected_chanes에 가까운 값을 선택합니다.
          if trading_volume > 0:
            fiat_correct_threshold = geographical_interpolate(max(abs(expected_changes), 1), trading_volume, 0.8, 0.2)
            is_correct &= abs(actual_changes) < fiat_correct_threshold

            log = "Fiat [{0}] Balance Check after trade - expected_changes: {1:.6f}, trading_volume : {2:.6f}, " \
                  "fiat_correct_threshold: {3:.6f}, actual_changes: {4:.6f}".format(equity, expected_changes, trading_volume, fiat_correct_threshold, actual_changes)
            self.logger.info(log)
          else:
            # trading_volume이 0이 나오는 경우는 현재 binance:bnb 밖에 없습니다. 일단 무조건 correct로 취급합니다.
            pass
        else:
          is_correct &= similar(expected_changes, actual_changes, margin_of_error=crypto_margin_of_error)

          log = "Crypto [{0}] Balance Check after trade - expected_changes: {1:.6f}, actual_changes: {2:.6f}".format(
            equity, expected_changes, actual_changes)
          self.logger.info(log)

      if not is_correct:
        retry_count += 1
      else:
        break

    # 자산 정보를 업데이트한다.
    self.before_balance = before_balance
    self.after_balance = after_balance

    # 자산이 제대로 업데이트되었는지 여부를 리턴한다.
    return is_correct

  @property
  def participating_equities(self):
    # 현재 거래에 의해 변경되는 모든 asset의 집합을 만들어낸다.
    participating_equities = set()

    for task in self.tasks:
      [participating_equities.add(asset) for asset in task.participating_equities()]
      if task.chain_node.is_binance_exchange:
        participating_equities.add('binance:bnb')
    return participating_equities


class TradeTaskBundleExecutionResult(object):
  def __init__(self, market_ctx, graph, tasks):
    self.market_ctx = market_ctx
    self.graph = graph
    self.tasks = tasks
    self.before_balance = None
    self.after_balance = None
    self.is_balance_updated_correctly = False

  @property
  def is_trade_execution_succeed(self):
    for task in self.tasks:
      if task.status != TradeTaskStatus.SUCCESS:
        return False
    return True

  @property
  def is_transfer_needed(self):
    changes = self.balance_changes
    for change in changes:
      if change.is_transfer_needed:
        return True
    return False

  @property
  def balance_changes(self):
    equities = self.participating_equities
    equities = sorted(equities, key=lambda x: to_comparable_repr(x))

    changes = []
    for equity in equities:
      old_asset_volume = self.before_balance.assets[equity].volume
      new_asset_volume = self.after_balance.assets[equity].volume
      diff = new_asset_volume - old_asset_volume
      change = TradeTaskAssetChange()
      change.equity = equity
      change.volume = new_asset_volume
      change.diff = diff
      changes.append(change)
    return changes

  @property
  def total_balance_changes(self):
    equities = self.participating_equities

    total_changes_builder = {}
    for equity in equities:
      _, symbol = equity.split(':')
      old_asset_volume = self.before_balance.assets[equity].volume
      new_asset_volume = self.after_balance.assets[equity].volume
      diff = new_asset_volume - old_asset_volume
      if symbol not in total_changes_builder:
        change = TradeTaskAssetChange()
        change.equity = symbol
        change.volume = 0
        change.diff = 0
        total_changes_builder[symbol] = change
      change = total_changes_builder[symbol]
      change.volume += new_asset_volume
      change.diff += diff
    changes = total_changes_builder.values()
    return sorted(changes, key=lambda x: to_comparable_repr(x.equity))

  @property
  def total_profit(self):
    usd_krw_price = self.market_ctx.usd_krw_price
    bnb_krw_price = usd_krw_price * self.market_ctx.orderbooks['binance:bnb/usdt'].ask0_price

    changes = self.total_balance_changes
    profit = 0
    for change in changes:
      if change.equity == 'krw':
        profit += change.diff
      if change.equity in ['usd', 'usdt']:
        # 좀 맘에 안들긴 하지만 usdt를 usd랑 똑같이 취급합니다.
        profit += change.diff * usd_krw_price
      if change.equity == 'bnb':
        profit += change.diff * bnb_krw_price
    return profit

  @property
  def participating_equities(self):
    chain = self.graph.chain

    equities = chain.participating_equities(with_exchange=True)
    if chain.contains_binance_exchange:
      # chain에 binance가 추가되어 있을 경우 여기에 bnb 를 강제로 추가시켜야 함 (fee deduct 때문에)
      equities.append('binance:bnb')

    return equities

  @property
  def participating_symbols(self):
    chain = self.graph.chain
    equities = chain.participating_equities(with_exchange=False)
    return equities

  @property
  def total_symbol_balance_changes(self):
    symbols = self.participating_symbols

    total_changes_builder = {}
    for equity in self.before_balance.assets:
      _, symbol = equity.split(':')
      if symbol not in symbols:
        continue

      old_asset_volume = self.before_balance.assets[equity].volume
      new_asset_volume = self.after_balance.assets[equity].volume
      diff = new_asset_volume - old_asset_volume
      if symbol not in total_changes_builder:
        change = TradeTaskAssetChange()
        change.equity = symbol
        change.volume = 0
        change.diff = 0
        total_changes_builder[symbol] = change
      change = total_changes_builder[symbol]
      change.volume += new_asset_volume
      change.diff += diff
    changes = total_changes_builder.values()
    return sorted(changes, key=lambda x: to_comparable_repr(x.equity))

  def total_symbol_balance(self, symbol):
    """
    :param symbol: equity without exchange
    :return:
    """
    volume = 0
    for equity in self.after_balance.assets:
      _, equity_symbol = equity.split(':')
      if symbol == equity_symbol:
        volume += self.after_balance.assets[equity].volume
    return volume


class TradeTaskAssetChange(object):
  __slots__ = (
    'equity',
    'volume',
    'diff',
  )

  @property
  def is_transfer_needed(self):
    """
    현재 이 자산의 변화로 송금이 필요한지 여부를 확인한다.
    """
    # 이번 트레이드로 인해 이 자산이 소모되었고,
    # 자산의 남은 volume이 이번에 변경된 값의 1/10보다 작게 남았으면
    # 전송이 필요한 것으로 생각한다.
    return self.diff < 0 and self.volume < abs(self.diff) / 10.0
