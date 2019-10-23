# -*- coding: utf-8 -*-
import logging

from gevent import monkey

monkey.patch_all()

import gevent
import requests.adapters
from carbi.loop import Looper
from carbi.injector import Injector
from carbi.module.tracker import MarketContextTracker
from carbi.module.handler.bigquery_streamer import BigQueryStreamer
from carbi.module.handler.inspect_market_context import InspectMarketContextHandler
from carbi.module.trade.chain import Chains, get_orderbook_keys
from carbi.module.tracker.target import build_targets

sess = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_maxsize=100, max_retries=10)
sess.mount('https://', adapter)

chains = Chains.load_from_file('./conf/chain/inspector.txt')
injector = Injector.create('./conf/carbi.yaml')
orderbook_keys = get_orderbook_keys(Chains.load_from_file('./conf/chain/seeker.txt'))
targets = build_targets(orderbook_keys=orderbook_keys, with_okex_futures=True)
market_tracker = MarketContextTracker(injector=injector, targets=targets)
logger = injector.logger

channels = injector.channels
channels.init_with_chains(chains)
channels.start()
handlers = [
  InspectMarketContextHandler(injector=injector, chains=chains),
  BigQueryStreamer(injector=injector),
]


def run():
  try:
    run_internal()
  except Exception as e:
    logger.error(e, exc_info=True)
    gevent.sleep(10)


def run_internal():
  global market_tracker, handlers
  if not market_tracker.update():
    # 업데이트에 실패한 경우 나중에 다시 시도한다.
    return
  market_ctx = market_tracker.get()

  for handler in handlers:
    handler.handle(market_ctx)


if __name__ == '__main__':
  logging.basicConfig()
  lopper = Looper(delay_millis=30000)
  lopper.loop(run)
