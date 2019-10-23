# -*- coding: utf-8 -*-
import logging

from gevent import monkey

monkey.patch_all()

import gevent
from carbi.config import CarbiConfigKeys
from carbi.dummy import build_wealthy_balance_ctx
from carbi.loop import Looper
from carbi.injector import Injector
from carbi.module.trade import ProfitSeeker
from carbi.module.trade.chain import Chains, get_orderbook_keys
from carbi.module.tracker import MarketContextTracker
from carbi.module.tracker.target import build_targets

chains = Chains.load_from_file('./conf/chain/seeker.txt')
injector = Injector.create('./conf/carbi.yaml')
orderbook_keys = get_orderbook_keys(chains)
targets = build_targets(orderbook_keys=orderbook_keys, with_okex_futures=True)
market_tracker = MarketContextTracker(injector=injector, targets=targets)
seeker = ProfitSeeker(injector=injector)
logger = injector.logger


def run():
  try:
    run_internal()
  except Exception as e:
    logger.info('Skipped')
    gevent.sleep(10)


def run_internal():
  global market_tracker
  if not market_tracker.update():
    # 업데이트에 실패한 경우 나중에 다시 시도한다.
    return
  market_ctx = market_tracker.get()
  balance_ctx = build_wealthy_balance_ctx(chains)

  # 여러 조건에 따라 이득이 되는 거래를 찾아본다.
  bundles = seeker.find_profitable_trade_bundles(chains, market_ctx, balance_ctx)
  if len(bundles) == 0:
    logger.info('Nothing')
    return

  for bundle in bundles:
    if bundle.graph.total_profit_margin() > 0:
      chain = bundle.graph.chain
      profit_margin = bundle.graph.total_profit_margin() * 100.0
      total_profit = bundle.graph.total_profit()
      if 'korbit' not in str(bundle.graph.chain) and 'coinone' not in str(bundle.graph.chain):
        logger.info('{0} - {1:.3f} % - {2:.3f} USD'.format(chain, profit_margin, total_profit))
      else:
        logger.info('{0} - {1:.3f} % - {2:.0f} KRW'.format(chain, profit_margin, total_profit))


if __name__ == '__main__':
  delay_millis = injector.config[CarbiConfigKeys.LOOP_DELAY_MILLIS]
  logging.basicConfig()
  lopper = Looper(delay_millis=delay_millis)
  lopper.loop(run)
