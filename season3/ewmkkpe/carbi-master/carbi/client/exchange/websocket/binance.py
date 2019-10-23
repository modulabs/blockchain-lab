# -*- coding: utf-8 -*-
import json
import re

import websocket

from carbi.client.exchange.http.binance import EQUITY_PAIRS, BinanceParser

BINANCE_WEBSOCKET_ENDPOINT = 'wss://stream.binance.com:9443'
WEBSOCKET_VALID_ORDERBOOK_LIMIT = [5, 10, 20]


class BinanceWebSocketClient(object):
  """
  1초에 한번씩 업데이트 되는 Orderbook을 가져오는 데만 사용할 수 있다.
  """

  def __init__(self, config):
    self.config = config
    self.ws = None
    self.callback = None
    self.orderbooks = {}

  def subscribe_orderbooks_until_closed(self, equity_pairs=[], depth=20):
    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/web-socket-streams.md#partial-book-depth-streams
    assert len(equity_pairs) > 0, 'There should be more than 1 equity_pairs'
    assert depth in WEBSOCKET_VALID_ORDERBOOK_LIMIT, 'Depth should be one of {}'.format(WEBSOCKET_VALID_ORDERBOOK_LIMIT)

    endpoint = self._orderbooks_susbscribe_endpoint(equity_pairs, depth)

    assert self.ws is None
    self.ws = websocket.WebSocketApp(
      endpoint,
      on_message=self._handle_message,
      on_error=self._handle_error,
      on_close=self._handle_close
    )
    # 연결이 끊어지면 run_forever는 종료된다.
    self.ws.run_forever(
      origin=endpoint,
      ping_interval=5,
      ping_timeout=4
    )

  def _orderbooks_susbscribe_endpoint(self, equity_pairs, depth=20):
    exchange_pairs = map(lambda equity_pair: EQUITY_PAIRS.to_exchange_pair(equity_pair), equity_pairs)
    streams_strings = map(lambda exchange_pair: '{}@depth{}'.format(exchange_pair.lower(), depth), exchange_pairs)
    streams_string = '/'.join(streams_strings)
    return BINANCE_WEBSOCKET_ENDPOINT + '/stream?streams={}'.format(streams_string)

  def _handle_message(self, ws, m):
    message = json.loads(m)

    # only support Partial Book Depth Streams
    stream = message['stream']  # in the form of ethbtc@depth20
    data = message['data']
    binance_equity_pair, _ = self._parse_stream_response(stream)

    orderbook = BinanceParser.parse_orderbook_response(response=data, binance_equity_pair=binance_equity_pair)
    equity_pair = EQUITY_PAIRS.from_exchange_pair(binance_equity_pair)
    self.orderbooks[equity_pair] = orderbook

  def get_orderbook(self, equity_pair):
    if equity_pair in self.orderbooks:
      return self.orderbooks[equity_pair]
    else:
      return None

  def _parse_stream_response(self, stream):
    """
    :param stream: ethbtc@depth20, ...
    :return: tuple of (string, int). ex) (ETHBTC, 20)
    """
    m = re.search(r'(\w+)@depth(\d+)', stream)
    if m:
      return m.group(1).upper(), int(m.group(2))
    else:
      raise ValueError("Can't parse stream name : {}".format(stream))

  def _handle_error(self, ws, error):
    if self.ws == ws:
      self.ws = None
    print '_handle_error'
    print error

  def _handle_close(self, ws):
    if self.ws == ws:
      self.ws = None
    print '_handle_close'
