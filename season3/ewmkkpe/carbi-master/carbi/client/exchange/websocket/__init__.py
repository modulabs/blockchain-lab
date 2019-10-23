# -*- coding: utf-8 -*-

import websocket

from carbi.client.exchange.utils import callback


class WebSocketClient(object):
  def __init__(self, endpoint):
    self.endpoint = endpoint
    self.ws = None
    self.on_error = None
    self.on_close = None

  def run_until_closed(self):
    """
    웹소켓 연결은 맺고 이벤트가 올떄마다 콜백을 호출한다.
    연결이 끊어지면 적절한 콜백을 호출한 후, 이 함수가 종료된다.
    """
    assert self.ws is None
    self.ws = websocket.WebSocketApp(
      self.endpoint,
      on_message=self.on_receive_message,
      on_error=self.on_error,
      on_close=self.on_close,
    )
    # 연결이 끊어지면 run_forever는 종료된다.
    self.ws.run_forever(
      origin=self.endpoint,
      ping_interval=5,
      ping_timeout=4
    )
    # 연결이 끊어지면 이 코드가 실행된다.
    # ws를 None으로 만들고 끝낸다.
    self.ws = None

  def send(self, request):
    """
    웹소켓 연결로 요청을 보낸다.
    응답은 on_receive_message을 통해 온다.
    나중에 id->Callback 맵을 이용해 응답을 여기서 리턴으로 주면 좋을 듯.
    """
    self.ws.send(request)

  @callback
  def on_receive_message(self, ws, msg):
    """
    윕소켓 연결로부터 메시지를 받게 된경우 이 함수를 호출한다.
    이 클래스를 상송 받는 경우 이 함수를 구현해야한다.
    """
    pass
