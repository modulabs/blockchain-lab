# -*- coding: utf-8

from carbi.utils import ts


class Orderbook(object):
  def __init__(self, exchange, equity_pair, asks=None, bids=None, timestamp=None):
    """
    :param exchange: String
    :param equity_pair: btc/usd, btc/krw, eth/btc, ...
    :param asks: List of {'price': float, 'volume': float}, first price is the best price to market buy
    :param bids: List of {'price': float, 'volume': float}, first price is the best price to market sell
    :param timestamp: 13 digit ms information, from exchange optionally
    :param response: response of exchange itself
    """
    if bids is None:
      bids = []
    if asks is None:
      asks = []
    if timestamp is None:
      timestamp = ts()
    self.exchange = exchange
    self.equity_pair = equity_pair
    self.asks = asks
    self.bids = bids
    self.timestamp = timestamp

  @property
  def key(self):
    return '%s:%s' % (self.exchange, self.equity_pair)

  @property
  def ask0_price(self):
    return self.asks[0]['price']

  @property
  def bid0_price(self):
    return self.bids[0]['price']

  @property
  def ask0_volume(self):
    return self.asks[0]['volume']

  @property
  def bid0_volume(self):
    return self.bids[0]['volume']

  def to_bigquery_struct(self, snapshot_ts):
    return dict(
      key=self.key,
      exchange=self.exchange,
      equity_pair=self.equity_pair,
      ask0_price=self.ask0_price,
      ask0_volume=self.ask0_volume,
      asks=self.asks,
      bid0_price=self.bid0_price,
      bid0_volume=self.bid0_volume,
      bids=self.bids,
      ts=self.timestamp / 1000,
      snapshot_ts=snapshot_ts,
      created=ts() / 1000,
    )

  def __str__(self):
    return "Orderbook(%s:%s bids[0:%s] asks[0:%d])" % (self.exchange, self.equity_pair, len(self.bids), len(self.asks))

  def __repr__(self):
    return self.__str__()
