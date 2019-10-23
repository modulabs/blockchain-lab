# -*- coding: utf-8 -*-
from carbi.cmp import to_comparable_repr
from carbi.module.trade.chain import get_orderbook_keys
from carbi.utils.okex import get_future_expiry_symbol


class OrderbookSpread(object):
  __slots__ = (
    'orderbook_key',
    'spread',
  )

  @property
  def exchange(self):
    return self.orderbook_key.split(':')[0]

  @staticmethod
  def build_orderbook_spreads(chains, market_ctx):
    orderbook_keys = get_orderbook_keys(chains)
    orderbook_spreads = []
    for orderbook_key in orderbook_keys:
      if not orderbook_key in market_ctx.orderbooks:
        continue
      orderbook = market_ctx.orderbooks[orderbook_key]
      ask = orderbook.asks[0]['price']
      bid = orderbook.bids[0]['price']
      spread = (ask - bid) / ((ask + bid) / 2)

      orderbook_spread = OrderbookSpread()
      orderbook_spread.orderbook_key = orderbook_key
      orderbook_spread.spread = spread
      orderbook_spreads.append(orderbook_spread)
    return orderbook_spreads


class TransferRatio(object):
  __slots__ = (
    'chain',
    'ratio',
    'price_diff',
  )

  @property
  def exchange_pair(self):
    exchange_pair = [self.chain.nodes[0].exchange, self.chain.nodes[2].exchange]
    exchange_pair = sorted(exchange_pair, key=to_comparable_repr)
    return ':'.join(exchange_pair)

  @property
  def equity(self):
    return self.chain.nodes[0].input_equity(with_exchange=True)

  @staticmethod
  def build_transfer_ratio(chain, market_ctx):
    assert len(chain.nodes) == 3
    assert chain.nodes[0].action == 'sell'
    assert chain.nodes[0].output_equity() in ['usd', 'krw']
    assert chain.nodes[1].exchange == 'currency'
    assert chain.nodes[2].action == 'buy'
    assert chain.nodes[2].input_equity() in ['krw', 'usd']

    profit_rate = 1

    # 팔기: sell(coinone:eth/krw)
    orderbook_key = chain.nodes[0].orderbook_key
    if not orderbook_key in market_ctx.orderbooks:
      trade_ratio = TransferRatio()
      trade_ratio.chain = chain
      trade_ratio.ratio = 1
      trade_ratio.price_diff = 0
      return trade_ratio
    orderbook = market_ctx.orderbooks[orderbook_key]
    unit = orderbook.bids[0]
    bid = unit['price']
    profit_rate *= bid

    # 환전하기: sell(currency:krw/usd)
    currency_exchange_action = chain.nodes[1].action
    usd_krw_price = market_ctx.usd_krw_price
    if currency_exchange_action == 'buy':
      profit_rate *= usd_krw_price
    else:
      profit_rate /= usd_krw_price

    # 사기: buy(cex:eth/usd)
    orderbook_key = chain.nodes[2].orderbook_key
    if not orderbook_key in market_ctx.orderbooks:
      trade_ratio = TransferRatio()
      trade_ratio.chain = chain
      trade_ratio.ratio = 1
      trade_ratio.price_diff = 0
      return trade_ratio
    orderbook = market_ctx.orderbooks[orderbook_key]
    unit = orderbook.asks[0]
    ask = unit['price']
    profit_rate /= ask

    # 두 거래소간의 가격 차이를 계산해준다.
    # currency_exchange_action가 buy인 경우는 chain에서 처음 파는 부분이 cex인 경우이다.
    price_diff = bid * usd_krw_price - ask if currency_exchange_action == 'buy' else bid - ask * usd_krw_price

    trade_ratio = TransferRatio()
    trade_ratio.chain = chain
    trade_ratio.ratio = profit_rate
    trade_ratio.price_diff = price_diff
    return trade_ratio


class FuturePremium(object):
  __slots__ = (
    'symbol',
    'ratio',
    'price_diff',
    'spot_price',
    'future_price',
  )

  @property
  def equity(self):
    return 'okex:{}'.format(self.symbol)

  @staticmethod
  def build_future_premium(symbol, market_ctx):
    spot_orderbook_key = 'okex:{}/usdt'.format(symbol)
    future_orderbook_key = 'okex:f_{}/usd_{}'.format(symbol, get_future_expiry_symbol('quarter'))
    print spot_orderbook_key
    print future_orderbook_key
    ratio = 1
    price_diff = 0
    if spot_orderbook_key in market_ctx.orderbooks and future_orderbook_key in market_ctx.orderbooks:
      spot_orderbook = market_ctx.orderbooks[spot_orderbook_key]
      future_orderbook = market_ctx.orderbooks[future_orderbook_key]

      # 일반적으로 선물이 현물보다 더 비싸야 한다.
      if spot_orderbook.ask0_price < future_orderbook.bid0_price:
        price_diff = future_orderbook.bid0_price - spot_orderbook.ask0_price
        ratio = future_orderbook.bid0_price / spot_orderbook.ask0_price
      else:
        price_diff = future_orderbook.ask0_price - spot_orderbook.bid0_price
        ratio = future_orderbook.ask0_price / spot_orderbook.bid0_price
    future_premium = FuturePremium()
    future_premium.symbol = symbol
    future_premium.ratio = ratio
    future_premium.price_diff = price_diff
    return future_premium
