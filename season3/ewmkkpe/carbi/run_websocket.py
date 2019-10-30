# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()

import gevent
import logging
from carbi.injector import Injector
from carbi.module.channel import ChannelProvider
from carbi.module.trade.chain import Chains

if __name__ == '__main__':
  logging.basicConfig()
  injector = Injector.create('./conf/carbi.yaml')
  chains = Chains.load_from_file('./conf/chain/seeker.txt')
  channels = ChannelProvider(injector)
  channels.init_with_chains(chains)
  channels.start()
  print('connect...')
  gevent.sleep(3)


  def buy():
    channel = channels.get_channel_or_none('cex')
    r = channel.place_buy_order(equity_pair='xrp/usd', amount=0, price=1)
    print r


  def sell():
    channel = channels.get_channel_or_none('cex')
    r = channel.place_sell_order(equity_pair='xrp/usd', amount=0, price=0.9)
    print r


  e1 = gevent.spawn(buy)
  e2 = gevent.spawn(buy)
  gevent.joinall([e1, e2])

  e1 = gevent.spawn(sell)
  e2 = gevent.spawn(sell)
  gevent.joinall([e1, e2])
