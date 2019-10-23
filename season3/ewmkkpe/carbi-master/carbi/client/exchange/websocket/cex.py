# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
from Queue import Queue

from carbi.client.exchange.http.cex import CexResponseHandler
from carbi.client.exchange.nonce import NonceIssuer
from carbi.client.exchange.utils import public, private, callback
from carbi.client.exchange.websocket import WebSocketClient
from carbi.struct.orderbook import Orderbook
from carbi.utils import ts
import gevent

CEX_WEBSOCKET_ENDPOINT = 'wss://ws.cex.io/ws/'


class CexWebSocketOrderIdIssuer(object):
  def __init__(self):
    self.nonce_issuer = NonceIssuer()

  def next_order_id(self):
    nonce = self.nonce_issuer.next_nonce()
    return "oid-{}".format(nonce)


class CexWebSocketConsumer(object):
  def __init__(self, client, logger):
    # TODO(Andrew): maybe introduce state on consumer or partitioning consumer based on equity_pair
    self.client = client
    self.logger = logger
    self.orderbooks = {}
    self.last_updated_ts = 0
    self.last_ids = {}
    self.depths = {}

  def init_orderbook(self, equity_pair, depth):
    self.orderbooks[equity_pair] = {
      'asks': {},
      'bids': {},
      'timestamp': ts(),
    }
    if equity_pair in self.last_ids:
      del self.last_ids[equity_pair]
    self.depths[equity_pair] = depth

  def deregister_orderbook(self, equity_pair):
    if equity_pair in self.orderbooks:
      del self.orderbooks[equity_pair]
    if equity_pair in self.last_ids:
      del self.last_ids[equity_pair]
    if equity_pair in self.depths:
      del self.depths[equity_pair]

  def offer_orderbook(self, message):
    id = message['data']['id']
    pair = message['data']['pair']
    pairs = pair.split(':')
    equity_pair = '{}/{}'.format(pairs[0].lower(), pairs[1].lower())

    if not self._check_id_increment(equity_pair, id, True):
      prev_id = self.last_ids[equity_pair]
      self.logger('Check id increment failed. {} expected, but {} found on {}'.format(prev_id + 1, id, equity_pair))

      # 이게 blocking call이라 별도의 greenlet으로 하는게 좋을 듯
      gevent.spawn(self.resubscribe_orderbook, equity_pair)
      return

    if equity_pair not in self.orderbooks:
      return

    orderbook = self.orderbooks[equity_pair]
    timestamp = message['data']['timestamp']  # in second
    orderbook['timestamp'] = timestamp * 1000

    asks = message['data']['asks']
    bids = message['data']['bids']
    for ask in asks:
      price = ask[0]
      volume = ask[1]
      orderbook['asks'][price] = volume
    for bid in bids:
      price = bid[0]
      volume = bid[1]
      orderbook['bids'][price] = volume
    self.last_updated_ts = ts()

  def offer_orderbook_update(self, message):
    id = message['data']['id']
    pair = message['data']['pair']
    pairs = pair.split(':')
    equity_pair = '{}/{}'.format(pairs[0].lower(), pairs[1].lower())

    if not self._check_id_increment(equity_pair, id, False):
      self.logger('Check id increment failed. {} expected, but {} found on {}'.format(prev_id + 1, id, equity_pair))

      # 이게 blocking call이라 별도의 greenlet으로 하는게 좋을 듯
      gevent.spawn(self.resubscribe_orderbook, equity_pair)
      return

    if equity_pair not in self.orderbooks:
      return

    orderbook = self.orderbooks[equity_pair]
    timestamp = message['data']['time']  # in ms
    orderbook['timestamp'] = timestamp

    asks = message['data']['asks']
    bids = message['data']['bids']
    for ask in asks:
      price = ask[0]
      volume = ask[1]
      if volume == 0:
        if price in orderbook['asks']:
          del orderbook['asks'][price]
      else:
        orderbook['asks'][price] = volume
    for bid in bids:
      price = bid[0]
      volume = bid[1]
      if volume == 0:
        if price in orderbook['bids']:
          del orderbook['bids'][price]
      else:
        orderbook['bids'][price] = volume
    self.last_updated_ts = ts()

  def _check_id_increment(self, equity_pair, id, is_first):
    if equity_pair not in self.last_ids:
      if is_first:
        self.last_ids[equity_pair] = id
      return True
    else:
      last_id = self.last_ids[equity_pair]
      if last_id + 1 != id:
        return False
      else:
        self.last_ids[equity_pair] = id
        return True

  def resubscribe_orderbook(self, equity_pair):
      depth = self.depths[equity_pair]
      self.client.unsubscribe_orderbook(equity_pair)
      self.client.subscribe_orderbook(equity_pair, depth)

  def get_current_orderbook(self, equity_pair, depth):
    current_ts = ts()
    connected = current_ts - self.last_updated_ts < 500
    if not connected:
      return None
    if equity_pair not in self.orderbooks:
      return None
    if not (len(self.orderbooks[equity_pair]['asks']) > 0 and len(self.orderbooks[equity_pair]['bids']) > 0):
      return None

    cex_asks = self.orderbooks[equity_pair]['asks']
    cex_bids = self.orderbooks[equity_pair]['bids']
    timestamp = self.orderbooks[equity_pair]['timestamp']

    if current_ts - timestamp > 3000:
      # cex 서버 타임스탬프가 3초 이상 오래된 경우에는 최신이라고 확신할 수 없기 때문에 그냥 사용하지 않습니다.
      return None

    asks_result = []
    for ask_price in cex_asks:
      ask_volume = cex_asks[ask_price]
      asks_result.append([ask_price, ask_volume])
    asks_result.sort()
    asks_result = asks_result[0:min(depth, len(asks_result))]
    asks = map(lambda elem: {'price': elem[0], 'volume': elem[1]}, asks_result)

    bids_result = []
    for bid_price in cex_bids:
      bid_volume = cex_bids[bid_price]
      bids_result.append([bid_price, bid_volume])
    bids_result.sort(reverse=True)
    bids_result = bids_result[0:min(depth, len(bids_result))]
    bids = map(lambda elem: {'price': elem[0], 'volume': elem[1]}, bids_result)

    return Orderbook('cex', equity_pair=equity_pair, asks=asks, bids=bids, timestamp=timestamp)


class CexWebSocketClient(WebSocketClient):
  def __init__(self, config, logger):
    WebSocketClient.__init__(self, CEX_WEBSOCKET_ENDPOINT)
    self.config = config
    self.logger = logger
    self.order_id_issuer = CexWebSocketOrderIdIssuer()
    self.orderbook_consumer = CexWebSocketConsumer(self, logger)
    self.response_queues = dict()
    self.on_active = None

  @public
  def subscribe_orderbook(self, equity_pair, depth=0):
    order_id = self.order_id_issuer.next_order_id()
    self.orderbook_consumer.init_orderbook(equity_pair, depth)
    request = CexWebSocketClientRequests.build_subscribe_orderbook_request(equity_pair, depth, order_id)
    self.send(json.dumps(request))

  @public
  def unsubscribe_orderbook(self, equity_pair):
    order_id = self.order_id_issuer.next_order_id()
    self.orderbook_consumer.deregister_orderbook(equity_pair)
    request = CexWebSocketClientRequests.build_unsubscribe_orderbook_request(equity_pair, order_id)
    queue = Queue()
    self.response_queues[order_id] = queue
    self.send(json.dumps(request))
    try:
      response = queue.get(timeout=10)

      assert response['e'] == 'order-book-unsubscribe', 'Event Type is not matched : {}'.format((response['e']))
      pair = response['data']['pair']
      pairs = pair.split(':')
      response_equity_pair = '{}/{}'.format(pairs[0].lower(), pairs[1].lower())
      assert response_equity_pair == equity_pair, ''
    finally:
      # queue에서 꺼내다가 Timeout에 걸리거나 하면 Empty Exception이 발생한다.
      # 정상적으로 꺼내진 경우, Timeout나 경우 모두 response_queue는 삭제해버린다.
      del self.response_queues[order_id]
    CexResponseHandler.raise_if_exception(response['data'])
    return response

  @public
  def get_orderbook(self, equity_pair, depth=20):
    assert depth > 0, "depth must be positive"
    return self.orderbook_consumer.get_current_orderbook(equity_pair, depth)

  @private
  def place_buy_order(self, equity_pair, amount, price):
    order_id = self.order_id_issuer.next_order_id()
    request = CexWebSocketClientRequests.build_place_order_request('buy', equity_pair, amount, price, order_id)
    queue = Queue()
    self.response_queues[order_id] = queue
    self.send(json.dumps(request))
    try:
      response = queue.get(timeout=10)
    finally:
      # queue에서 꺼내다가 Timeout에 걸리거나 하면 Empty Exception이 발생한다.
      # 정상적으로 꺼내진 경우, Timeout나 경우 모두 response_queue는 삭제해버린다.
      del self.response_queues[order_id]
    CexResponseHandler.raise_if_exception(response['data'])
    return response

  @private
  def place_sell_order(self, equity_pair, amount, price):
    order_id = self.order_id_issuer.next_order_id()
    request = CexWebSocketClientRequests.build_place_order_request('sell', equity_pair, amount, price, order_id)
    queue = Queue()
    self.response_queues[order_id] = queue
    self.send(json.dumps(request))
    try:
      response = queue.get(timeout=10)
    finally:
      # queue에서 꺼내다가 Timeout에 걸리거나 하면 Empty Exception이 발생한다.
      # 정상적으로 꺼내진 경우, Timeout나 경우 모두 response_queue는 삭제해버린다.
      del self.response_queues[order_id]
    CexResponseHandler.raise_if_exception(response['data'])
    return response

  @callback
  def on_receive_message(self, ws, msg):
    message = json.loads(msg)
    if 'e' not in message:
      return
    evt = message['e']
    if evt == 'connected':
      # 처음 연결이 맺어지면 connected 이벤트가 내려온다.
      # 연결이 맺어지는 즉시 바로 Authenticate 요청을 날린다.
      key = self.config.key
      secret = self.config.secret
      request = CexWebSocketClientRequests.build_authenticate_request(key, secret)
      self.send(json.dumps(request))
      return
    elif evt == 'auth':
      # Authenticate에 대한 응답을 처리한다.
      # 만약 실패하면 그냥 그대로 Raise해준다.
      self.close_if_error(ws, message)
      assert self.on_active is not None
      self.on_active(ws)
      return
    elif evt == 'order-book-subscribe':
      self.close_if_error(ws, message)
      self.orderbook_consumer.offer_orderbook(message)
      return
    elif evt == 'md_update':
      self.orderbook_consumer.offer_orderbook_update(message)
      return
    elif evt == 'ping':
      self.send(json.dumps(CexWebSocketClientRequests.build_pong_request()))
      return
    else:
      # 만약 message에 oid가 있고, oid에 해당하는 response_queue가 있다면,
      # oid에 해당하는 response_queue를 가져와서 response객체를 넣어준다.
      # 그러면 요청을 날린쪽에서 해당 response를 받아서 처리하게 된다.
      if 'oid' not in message:
        return
      oid = message['oid']
      # 그냥 이렇게 에러를 내도 웹소켓 연결이 끊어지거나 하지는 않고 그냥 로깅만 된다.
      assert oid in self.response_queues, '{}: no response_queue'.format(oid)
      queue = self.response_queues[oid]
      queue.put_nowait(message)

  @staticmethod
  def close_if_error(ws, message):
    try:
      assert message['ok'] == 'ok'
    except:
      ws.close()


class CexWebSocketClientRequests(object):
  @staticmethod
  def build_authenticate_request(key, secret):
    timestamp = int(ts() / 1000)
    nonce_with_key = "{}{}".format(timestamp, key)
    signature = hmac.new(secret.encode(), nonce_with_key.encode(), hashlib.sha256).hexdigest()
    return {
      'e': 'auth',
      'auth': {
        'key': key,
        'signature': signature,
        'timestamp': timestamp,
      },
      'oid': 'auth'
    }

  @staticmethod
  def build_subscribe_orderbook_request(equity_pair, depth, order_id):
    equities = equity_pair.split('/')
    return {
      "e": "order-book-subscribe",
      "data": {
        "pair": [
          equities[0].upper(),
          equities[1].upper()
        ],
        "subscribe": True,
        "depth": depth
      },
      "oid": order_id
    }

  @staticmethod
  def build_unsubscribe_orderbook_request(equity_pair, order_id):
    equities = equity_pair.split('/')
    return {
      "e": "order-book-unsubscribe",
      "data": {
        "pair": [
          equities[0].upper(),
          equities[1].upper()
        ],
      },
      "oid": order_id
    }

  @staticmethod
  def build_place_order_request(action, equity_pair, amount, price, order_id):
    assert action in ['buy', 'sell']
    equities = equity_pair.split('/')
    return {
      "e": "place-order",
      "data": {
        "pair": [
          equities[0].upper(),
          equities[1].upper()
        ],
        "amount": amount,
        "price": price,
        "type": action
      },
      "oid": order_id
    }

  @staticmethod
  def build_pong_request():
    return {
      'e': 'pong'
    }
