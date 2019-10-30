# -*- coding: utf-8 -*-
import logging

from gevent import monkey

monkey.patch_all()

import sys
import gevent
from carbi.config import CarbiConfigKeys
from carbi.loop import Looper
from carbi.injector import Injector
from carbi.module.trade import ProfitSeeker
from carbi.module.trade.chain import Chains, get_orderbook_keys
from carbi.module.tracker import MarketContextTracker, BalanceContextTracker
from carbi.module.trade.notify import TradeNotifier
from carbi.module.balancer import AutomaticBalancer
from carbi.module.tracker.target import build_targets

chains = Chains.load_from_file('./conf/chain/trader.txt')
orderbook_keys = get_orderbook_keys(chains)
orderbook_keys.append('binance:bnb/usdt')

injector = Injector.create('./conf/carbi.yaml')
targets = build_targets(orderbook_keys=orderbook_keys, with_okex_futures=True)
market_tracker = MarketContextTracker(injector=injector, targets=targets)
balance_tracker = BalanceContextTracker(injector=injector)
seeker = ProfitSeeker(injector=injector)
notifier = TradeNotifier(injector=injector)
balancer = AutomaticBalancer.create(injector=injector, config_file_path='./conf/balance.yaml',
                                    market_tracker=market_tracker, balance_tracker=balance_tracker, notifier=notifier)
logger = injector.logger

channels = injector.channels
channels.init_with_chains(chains)
channels.start()


def before_run():
  global balance_tracker
  balance_tracker.update()


def run():
  try:
    run_internal()
  except Exception as e:
    logger.error(e, exc_info=sys.exc_info())
    gevent.sleep(10)

  try:
    balancer.run()
  except Exception as e:
    logger.error(e, exc_info=sys.exc_info())

  try:
    global market_tracker, balance_tracker
    market_ctx = market_tracker.get()
    balance_ctx = balance_tracker.get()
    notifier.notify_balance_status(market_ctx, balance_ctx)
  except Exception as e:
    logger.error(e, exc_info=sys.exc_info())


def run_internal():
  global market_tracker, balance_tracker
  if not market_tracker.update():
    # 업데이트에 실패한 경우 나중에 다시 시도한다.
    return
  if not balance_tracker.update_if_needed():
    # 업데이트에 실패한 경우 나중에 다시 시도한다.
    return
  market_ctx = market_tracker.get()
  balance_ctx = balance_tracker.get()

  # 여러 조건에 따라 이득이 되는 거래를 찾아본다.
  bundles = seeker.find_profitable_trade_bundles(chains, market_ctx, balance_ctx)
  bundles = filter_bundles(bundles)
  if len(bundles) == 0:
    logger.info('No profitable trade found.')
    return
  # 가장 이득이 되는 거래를 찾아 실행한다.
  bundle = select_bundles(bundles)
  result = bundle.execute(balance_tracker)
  notifier.notify_result(result)


def filter_bundles(bundles):
  # 너무 이익의 크기가 작은 경우는 무시한다.
  filtered_bundles = filter(lambda x: x.is_satisfy_profit_threshold, bundles)
  return filtered_bundles


def select_bundles(bundles):
  # 여기서 여러 가능한 TradeTaskBundle 중 하나를 선택한다.
  sorted_bundles = sorted(bundles, key=lambda x: x.graph.total_profit_margin(), reverse=True)
  return sorted_bundles[0]


if __name__ == '__main__':
  delay_millis = injector.config[CarbiConfigKeys.LOOP_DELAY_MILLIS]
  logging.basicConfig()
  before_run()
  lopper = Looper(delay_millis=delay_millis)
  lopper.loop(run)
