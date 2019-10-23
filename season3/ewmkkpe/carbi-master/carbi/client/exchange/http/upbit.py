# -*- coding: utf-8 -*-
import json
import random

import requests
import websocket

from carbi.client.exchange import sockjs
from carbi.client.exchange.constants import USER_AGENTS
from carbi.utils import ts

class UpbitConfiguration(object):
  __slots__ = (
    'auth_token',
  )

  def __repr__(self):
    return json.dumps(self.__dict__, indent=2)

  @staticmethod
  def load_from_file(conf_file):
    with open(conf_file, "r") as f:
      content = json.load(f)
      config = UpbitConfiguration()
      config.auth_token = content['auth_token']
      return config


class UpbitResponse:
  def __init__(self, response):
    self.status_code = response.status_code
    try:
      self.result = json.loads(response.text)
    except:
      print(response.text)
      self.result = {}


class UpbitClient(object):
  def __init__(self, conf):
    self.conf = conf

  def get_coin_prices(self):
    headers = {
      "Authorization": "Bearer %s" % self.conf.auth_token,
      "User-Agent": random.choice(USER_AGENTS)
    }
    url = 'https://crix-api-endpoint.upbit.com/v1/crix/recent?codes=CRIX.UPBIT.BTC-REP,CRIX.UPBIT.BTC-ZEC,CRIX.UPBIT.BTC-DASH,CRIX.UPBIT.BTC-XMR,CRIX.UPBIT.BTC-ARK,CRIX.UPBIT.BTC-LSK,CRIX.UPBIT.BTC-STORJ,CRIX.UPBIT.BTC-PIVX,CRIX.UPBIT.BTC-STEEM,CRIX.UPBIT.BTC-MTL,CRIX.UPBIT.BTC-VTC,CRIX.UPBIT.BTC-GRS,CRIX.UPBIT.BTC-KMD,CRIX.UPBIT.BTC-TIX,CRIX.UPBIT.BTC-LTC,CRIX.UPBIT.BTC-WAVES,CRIX.UPBIT.BTC-OMG,CRIX.UPBIT.BTC-ETH,CRIX.UPBIT.BTC-NEO,CRIX.UPBIT.BTC-BTG,CRIX.UPBIT.BTC-SBD,CRIX.UPBIT.BTC-ARDR,CRIX.UPBIT.BTC-XEM,CRIX.UPBIT.BTC-XLM,CRIX.UPBIT.BTC-POWR,CRIX.UPBIT.BTC-XRP,CRIX.UPBIT.BTC-ETC,CRIX.UPBIT.BTC-MER,CRIX.UPBIT.BTC-STRAT,CRIX.UPBIT.BTC-BCC,CRIX.UPBIT.BTC-SNT,CRIX.UPBIT.BTC-EMC2,CRIX.UPBIT.BTC-ADA,CRIX.UPBIT.BTC-QTUM'
    response = requests.get(url, headers=headers)
    return UpbitResponse(response)

  def get_coin_prices_with_codes(self, codes):
    url = 'https://crix-api-endpoint.upbit.com/v1/crix/recent?codes=%s' % codes
    headers = {
      "Authorization": "Bearer %s" % self.conf.auth_token,
      "User-Agent": random.choice(USER_AGENTS)
    }
    response = requests.get(url, headers=headers)
    return UpbitResponse(response)

  def get_my_assets(self):
    url = 'https://ccx.upbit.com/api/v1/investments/assets'
    headers = {
      "Authorization": "Bearer %s" % self.conf.auth_token,
      "User-Agent": random.choice(USER_AGENTS)
    }
    response = requests.get(url, headers=headers)
    return UpbitResponse(response)

  def post_order(self, market, bid_or_ask, volume, price):
    print('%s, %s, %f, %f' % (market, bid_or_ask, volume, price))
    url = 'https://ccx.upbit.com/api/v1/orders'
    headers = {
      "Authorization": "Bearer %s" % self.conf.auth_token,
      "User-Agent": random.choice(USER_AGENTS)
    }
    body = {"ord_type": "limit", "market": market, "side": bid_or_ask, "volume": volume, "price": price}
    response = requests.post(url, headers=headers, json=body)
    return UpbitResponse(response)

  def get_order_state(self, uuid):
    url = 'https://ccx.upbit.com/api/v1/order?uuid=%s' % uuid
    headers = {
      "Authorization": "Bearer %s" % self.conf.auth_token,
      "User-Agent": random.choice(USER_AGENTS)
    }
    response = requests.get(url, headers=headers)
    return UpbitResponse(response)

  def post_delete_order(self, uuid):
    print('delete %s' % uuid)
    url = 'https://ccx.upbit.com/api/v1/order?uuid=%s' % uuid
    headers = {
      "Authorization": "Bearer %s" % self.conf.auth_token,
      "User-Agent": random.choice(USER_AGENTS)
    }
    response = requests.delete(url, headers=headers)
    return UpbitResponse(response)

  def get_wating_orders(self):
    url = 'https://ccx.upbit.com/api/v1/orders?state=wait'
    headers = {
      "Authorization": "Bearer %s" % self.conf.auth_token,
      "User-Agent": random.choice(USER_AGENTS)
    }
    response = requests.get(url, headers=headers)
    return UpbitResponse(response)


class UpbitWebSocketClient(object):
  def __init__(self):
    self.info = {}
    self.handler = None
    self.codes = [
      'CRIX.UPBIT.KRW-BTC',
      'CRIX.UPBIT.BTC-ETH',
      'CRIX.UPBIT.BTC-BCC',
      'CRIX.UPBIT.BTC-BTG',
      'CRIX.UPBIT.KRW-ETH',
      'CRIX.UPBIT.KRW-BCC',
      'CRIX.UPBIT.KRW-BTG'
    ]

  def start(self):
    srv_id = sockjs.random_srv_id()
    conn_id = sockjs.random_conn_id()
    url = "wss://crix-websocket.upbit.com/sockjs/%s/%s/websocket" % (srv_id, conn_id)
    cookie = "__cfduid=decfe08ca8b274093bf97fac3547817681512839650; _ga=GA1.2.1982171562.1512839657; _gid=GA1.2.663680905.1514006453; JSESSIONID=dummy; cf_clearance=2430bc5aad5b5cd7c03acfb3726c6f13db96178f-1514010431-1800; _gat=1"
    header = ['User-Agent: %s' % (random.choice(USER_AGENTS))]
    ws = websocket.WebSocketApp(url, header=header, cookie=cookie)
    ws.on_message = self._handle_message
    ws.on_error = self._handle_error
    ws.on_close = self._handle_close
    ws.run_forever()

  def _request_info(self):
    url = "https://crix-websocket.upbit.com/sockjs/info?t=%s" % ts()
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    r = requests.get(url, headers=headers)
    self.info = r.json()

  def _subscribe(self, ws):
    ws.send(json.dumps([json.dumps([{
      'ticket': 'ram macbook'
    }, {
      'type': 'crixOrderbook',
      'codes': self.codes,
    }])]))

  def _handle_message(self, ws, message):
    if message == 'o':
      self._subscribe(ws)
    elif message[0] == 'a':
      entry = json.loads(json.loads(message[1:])[0])
      self._handle_entry(entry)

  def _handle_error(self, ws, error):
    print(error)

  def _handle_close(self, ws):
    print("### closed ###")

  def _handle_entry(self, entry):
    if self.handler:
      self.handler(entry)
