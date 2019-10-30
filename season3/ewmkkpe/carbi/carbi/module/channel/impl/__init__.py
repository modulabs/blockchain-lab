# -*- coding: utf-8 -*-
import gevent

from carbi.client.exchange.utils import public

BACKOFF_STEPS = [0, 1, 2, 3, 5, 10]


class Channel(object):
  def __init__(self, injector, client):
    self.logger = injector.logger
    self.client = client
    self.is_active = False
    self.retry_count = 0

  @public
  def start(self):
    gevent.spawn(self._run_forever)

  def _notify_active(self):
    """
    이 메서드는 Channel 구현체에서 적절히 호출해줘야한다.
    인증까지 완료해서 웹소켓 연결을 사용할 수 있는 상태가 되었을때 호출해줘야한다.
    """
    self.is_active = True
    # 인증까지 성공하면 재연결 BACKOFF를 초기화 시켜준다.
    self.retry_count = 0

  def _run_forever(self):
    while True:
      try:
        self.client.run_until_closed()
      finally:
        self.is_active = False
        idx = min(self.retry_count, len(BACKOFF_STEPS) - 1)
        gevent.sleep(BACKOFF_STEPS[idx])
        self.retry_count += 1
