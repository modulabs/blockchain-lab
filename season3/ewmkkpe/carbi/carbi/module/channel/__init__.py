# -*- coding: utf-8 -*-
from carbi.module.channel.impl.cex import CexChannel


class ChannelProvider(object):
  def __init__(self, injector):
    self.injector = injector
    self.channels = dict()

  def init_with_chains(self, chains):
    self.channels['cex'] = CexChannel.build(self.injector, chains)

  def start(self):
    for channel in self.channels.values():
      channel.start()

  def get_channel_or_none(self, exchange):
    """
    거래소에 대한 Active한 채널을 가져온다.
    연결이 끊어 진후, 인증이 된 후에 Active 상태가 된다.
    인증이 되지 않은 상태에선 Channel을 사용할 수 없는 것으로 간주한다.
    """
    if exchange not in self.channels:
      return None
    channel = self.channels[exchange]
    if not channel.is_active:
      return None
    return channel
