# -*- coding: utf-8 -*-
import sys
import gevent
from carbi.utils import ts
from carbi.utils import LimitedQueue
from carbi.module.trade.executor import TradeExecutorFactory
from carbi.module.balancer.rule import BalancingRules
from carbi.module.balancer.task import BalancingTask
from carbi.module.trade import TradeTask, TradeTaskBundle
from carbi.config import CarbiConfigKeys

MARKET_PRICE_MARGIN = 0.04  # market price는 언제나 4% 정도 더 싸거나 비싸게 부릅니다.


class AutomaticBalancer(object):
  def __init__(self, injector, market_tracker, balance_tracker, rules, notifier):
    self.injector = injector
    self.logger = injector.logger
    self.executor_factory = TradeExecutorFactory(injector)
    self.market_tracker = market_tracker
    self.balance_tracker = balance_tracker
    self.rules = rules
    self.notifier = notifier

    self.last_run = ts()
    # 지난 3tick 의 history만 기록합니다.
    self.task_history = LimitedQueue(self._balancer_tick_period)

  @property
  def _balancer_tick_period(self):
    return self.injector.config[CarbiConfigKeys.BALANCER_TICK_PERIOD]

  @property
  def _balancer_tick_millis(self):
    return self.injector.config[CarbiConfigKeys.BALANCER_TICK_MILLIS]

  @classmethod
  def create(cls, injector, config_file_path, market_tracker, balance_tracker, notifier):
    rules = BalancingRules.load_rules(config_file_path)
    return AutomaticBalancer(injector, market_tracker, balance_tracker, rules, notifier)

  def run(self):
    # 특정 시간에 한번씩만 돕니다.
    if self._is_next_tick():
      self.logger.info('Running Automatic Balancer...')
      self._update_last_run()

      tasks = self._find_balancing_tasks()
      self.task_history.insert(tasks)

      executable_tasks = self._filter_executable_tasks()

      if executable_tasks:
        self.logger.info('There are {} balancing tasks to run.'.format(len(executable_tasks)))
        self._execute(executable_tasks)

        # clear already executed balancing tasks
        self.task_history.clear()

  def _is_next_tick(self):
    # 10분에 한번씩 확인합니다.
    if ts() > self.last_run + self._balancer_tick_millis:
      return True
    else:
      return False

  def _update_last_run(self):
    self.last_run = ts()

  def _find_balancing_tasks(self):
    """
    :return: dictionary of {equity: BalancingTask}
    """
    balance = self.balance_tracker.get()

    equity_volumes = {}
    balancing_tasks = {}

    for exchange_equity in balance.assets:
      exchange, equity = exchange_equity.split(":")
      if equity not in equity_volumes:
        equity_volumes[equity] = 0

      equity_volumes[equity] += balance.assets[exchange_equity].volume

    for rule in self.rules:
      equity = rule.equity
      current_volume = equity_volumes[equity]
      balancing_task = rule.balancing_task(current_volume)
      if balancing_task is not None:
        balancing_tasks[balancing_task.chain_node.target_equity] = balancing_task

    return balancing_tasks

  def _filter_executable_tasks(self):
    if len(self.task_history) < self._balancer_tick_period:
      return []

    recent_tasks = self.task_history[0]

    executable_tasks = []

    # recent_tasks와 같은 종류의 equity 가 지난 MONITORING_TICKS - 1번의 tick에서도 존재하고 action이 같을 때 해당 작업을 executable_tasks로 취급합니다.
    for equity in recent_tasks:
      skip_this_equity = False

      recent_task = recent_tasks[equity]
      chain_node = recent_task.chain_node
      volume = recent_task.volume

      for before_tasks in self.task_history[1:]:
        if equity in before_tasks:
          before_task = before_tasks[equity]
          if before_task.chain_node != chain_node:
            skip_this_equity = True
            break
          if before_task.volume < volume:
            volume = before_task.volume
        else:
          skip_this_equity = True
          break

      if skip_this_equity:
        continue
      else:
        executable_task = BalancingTask(chain_node, volume, recent_task.rule)
        executable_tasks.append(executable_task)

    return executable_tasks

  def _execute(self, executable_tasks):
    """
    :param executable_tasks: list of BalancingTask
    :return:
    """
    for executable_task in executable_tasks:
      try:
        balance_ctx = self.balance_tracker.update_and_get()
        market_ctx = self.market_tracker.update_and_get()

        multi_graph = executable_task.convert_to_multi_graph(market_ctx, balance_ctx, self.injector.exchange_policies)
        bundle = TradeTaskBundle(self.injector, market_ctx, multi_graph)
        bundle.tasks = self._build_trade_tasks(multi_graph)

        result = bundle.execute(self.balance_tracker)
        self.notifier.notify_balancing_task_result(result, executable_task)

      except Exception as e:
        self._handle_exception(e)
        gevent.sleep(5)

  def _build_trade_tasks(self, multi_graph):
    # TODO(Andrew): merge with carbi.trade.__init__.py/ProfitSeeker/_build_trade_tasks
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
