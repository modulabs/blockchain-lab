# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()

import gevent
from carbi.client.exchange.http.okex import OkexClient, OkexConfiguration
from carbi.utils.okex import CONTRACT_TYPES, THIS_WEEK, NEXT_WEEK, QUARTER
import json


okex = None


def main():
  global okex
  conf_file = 'conf/credentials/okex.json'
  conf = OkexConfiguration.load_from_file(conf_file)
  okex = OkexClient(conf)

  eos_equity_pair = 'eos/usd'
  etc_equity_pair = 'etc/usd'

  orderbook_this_week = okex.get_future_orderbook(eos_equity_pair, THIS_WEEK)
  orderbook_quarter = okex.get_future_orderbook(eos_equity_pair, QUARTER)

  print prettify(okex.get_future_balance())
  print (orderbook_this_week.bid0_price + orderbook_this_week.ask0_price) / 2
  print prettify(okex.get_future_positions(eos_equity_pair, THIS_WEEK))

  print (orderbook_quarter.bid0_price + orderbook_quarter.ask0_price) / 2
  print prettify(okex.get_future_positions(eos_equity_pair, QUARTER))


def prettify(j):
  return json.dumps(j, indent=2)


if __name__ == '__main__':
  main()
