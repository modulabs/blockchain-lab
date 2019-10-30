# -*- coding: utf-8 -*-
import gevent

from carbi.utils import ts


class Looper(object):
  def __init__(self, delay_millis):
    self.delay_millis = delay_millis

  def loop(self, func):
    delay_millis = self.delay_millis
    last_executed = ts()
    while True:
      now = ts()
      if now < last_executed + delay_millis:
        delay_seconds = (delay_millis - (now - last_executed)) / 1000.0
        gevent.sleep(delay_seconds)

      # func를 호출하기 전에 last_executed를 업데이트해야한다.
      # func를 실행 시간에 상관없이 주기적으로 실행하기 위함이다
      # ex) 1초 주기일떄, func이 0.2초 걸렸다면, 0.8초 후에 호출되어야 한다.
      last_executed = ts()
      func()
