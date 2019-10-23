# -*- coding: utf-8 -*-
import json
import sys
import urllib2

import gevent

from carbi.cmp import to_comparable_repr
from carbi.struct.asset import Asset
from carbi.struct.context import MarketContext, BalanceContext
from carbi.struct.currency_exchange_rate import CurrencyExchangeRate
from carbi.module.tracker.task.orderbook import get_orderbook_task
from carbi.utils import ts
from carbi.utils.gevent_utils import gevent_map
from carbi.utils.lines import ContentLines

DEFAULT_ORDERBOOK_KEYS = (
  'cex:btc/usd',
  'cex:eth/usd',
  'cex:bch/usd',
  'cex:xrp/usd',
  'coinone:btc/krw',
  'coinone:eth/krw',
  'coinone:bch/krw',
  'coinone:xrp/krw',
)


class MarketContextTracker(object):
  def __init__(self, injector, targets=()):
    self.injector = injector
    self.logger = injector.logger
    self.market_ctx = MarketContext()
    self.targets = targets
    self.last_currency_exchange_rates_updated = 0

  def get(self):
    return self.market_ctx

  def update_and_get(self):
    assert self.update(), 'MARKET_CTX_UPDATE_ERROR: Error occurs during updating market_ctx'
    return self.market_ctx

  def update(self):
    succeed = True
    # Orderbook 정보를 조회하고 MarketCtx에 업데이트한다.
    # 만약 에러가 발생하면 예상할 수 없는 에러가 발생한 것이다.
    # 네트워크 에러나 장애로 조회를 못한 경우는 내부적을 처리되기 때문에 고려할 필요가 없다.
    try:
      self._update_orderbooks()
    except Exception as e:
      self.logger.error(e, exc_info=sys.exc_info())
      succeed = False
    # 환율 정보를 조회하고 MarketCtx에 업데이트한다.
    # 매번 업데이트하는 것은 아니고 내부적으로 특정 주기별로 업데이트를 하게 된다.
    try:
      self._update_currency_exchange_rates()
    except Exception as e:
      self.logger.error(e, exc_info=sys.exc_info())
      succeed = False
    return succeed

  def _update_orderbooks(self):
    tasks = map(lambda x: get_orderbook_task(self.injector, x), self.targets)

    # 모든 테스크를 실행시키고 AsyncResult 리스트를 받아온다.
    pairs = map(lambda t: (t, t.execute()), tasks)

    # 받아온 AsyncResult 리스트에서 Orderbook을 뽑아온다.
    # 여기서 Exception을 raise하게 되면 이번 loop 전체가 실패해버린다.
    # 에러를 무시하는 것은 성공적으로 가져온 Orderbook으로라도 가능한 거래를 할 수 있기 때문이다.
    # 예를 들면 coinone에서 Orderbook가져오는걸 실패해도 korbit과 cex로 가능한 거래가 있을 수 있다.
    orderbooks = {}
    for pair in pairs:
      task, result = pair
      try:
        orderbook = result.get()
        orderbooks[orderbook.key] = orderbook
      except KeyboardInterrupt:
        raise
      except Exception as e:
        # 이런 경우 서버 장애 등의 이유로 에러가 난 것일 수 있다.
        # 이런 경우까지 Sentry에 로그를 남기는것은 낭비이다.
        msg = 'GET_ORDER_BOOK_ERROR: [{}] {}'.format(task.target, e.message)
        self.logger.warn(msg)

    # 조회에 실패한 orderbook_key는 잘못된 거래를 방지하기 위해 삭제한다.
    # 삭제하지 않으면 outdated된 Orderbook이 남아있게 되므로 문제가 될 수 있다
    for key in self.market_ctx.orderbooks.keys():
      if key not in orderbooks:
        del self.market_ctx.orderbooks[key]
    # 새로 받아오는데 성공한 Orderbook들은 MarketContext에 적용한다.
    for key, orderbook in orderbooks.iteritems():
      self.market_ctx.orderbooks[key] = orderbook
    return orderbooks

  def _update_currency_exchange_rates(self):
    if not self._should_update_currency_exchange_rates():
      return
    currency_exchange_rates = {}
    local_ts = ts()
    url = 'https://openexchangerates.org/api/latest.json?app_id=131b61542a82492c9016648292d4994c&base=USD'
    currency_json = json.loads(urllib2.urlopen(url).read())
    rates = currency_json['rates']
    for currency, rate in rates.iteritems():
      equity_pair = '{}/usd'.format(currency.lower())
      r = CurrencyExchangeRate(equity_pair=equity_pair, rate=rate, timestamp=local_ts)
      currency_exchange_rates[equity_pair] = r
    for key, r in currency_exchange_rates.iteritems():
      self.market_ctx.currency_exchange_rates[key] = r
    self.last_currency_exchange_rates_updated = ts()
    return currency_exchange_rates

  def _should_update_currency_exchange_rates(self):
    now = ts()
    expired = now > self.last_currency_exchange_rates_updated + 5 * 60 * 1000
    has_currency_exchange_rates = len(self.market_ctx.currency_exchange_rates) > 0
    return expired or not has_currency_exchange_rates


class BalanceContextTracker(object):
  def __init__(self, injector):
    self.injector = injector
    self.logger = injector.logger
    self.balance_ctx = BalanceContext()
    self.last_updated = 0

  def get(self):
    return self.balance_ctx

  def update_and_get(self):
    assert self.update(), 'BALANCE_CTX_UPDATE_ERROR: Error occurs during updating balance_ctx'
    return self.balance_ctx

  def update_if_needed(self):
    if self._should_update_assets():
      return self.update()
    return True

  def update(self):
    succeed = True
    # 자산 정보를 조회하고 BalanceCtx에 업데이트한다.
    # 자산 정보 업데이트를 5번이나 재시도 했는데도 실패한 경우이다.
    try:
      self._update_assets()
    except Exception as e:
      self.logger.error(e, exc_info=sys.exc_info())
      succeed = False
    return succeed

  def _update_assets(self):
    try:
      assets = self._get_assets()
      for key, asset in assets.iteritems():
        self.balance_ctx.assets[key] = asset
    except Exception as e:
      raise

  def _should_update_assets(self):
    now = ts()
    expired = now > self.last_updated + 30 * 1000
    has_assets = len(self.balance_ctx.assets) > 0
    return expired or not has_assets

  def _get_assets(self, max_retry_count=5):
    now = ts()
    assets = {}
    retry_count = 0
    while retry_count < max_retry_count:
      try:
        clients = [self.injector.coinone_client, self.injector.cex_client, self.injector.binance_client]
        # parallelize get_balance call
        rs = gevent_map(lambda client: client.get_balance(), clients)

        # coinone balance
        r = rs[0]
        assets['coinone:krw'] = Asset('coinone', 'krw', float(r['krw']['avail']), now)
        assets['coinone:btc'] = Asset('coinone', 'btc', float(r['btc']['avail']), now)
        assets['coinone:eth'] = Asset('coinone', 'eth', float(r['eth']['avail']), now)
        assets['coinone:bch'] = Asset('coinone', 'bch', float(r['bch']['avail']), now)
        assets['coinone:xrp'] = Asset('coinone', 'xrp', float(r['xrp']['avail']), now)

        # cex balance
        r = rs[1]
        assets['cex:usd'] = Asset('cex', 'usd', float(r['USD']['available']), now)
        assets['cex:btc'] = Asset('cex', 'btc', float(r['BTC']['available']), now)
        assets['cex:eth'] = Asset('cex', 'eth', float(r['ETH']['available']), now)
        assets['cex:bch'] = Asset('cex', 'bch', float(r['BCH']['available']), now)
        assets['cex:xrp'] = Asset('cex', 'xrp', float(r['XRP']['available']), now)

        # binance balance
        r = rs[2]
        assets['binance:usdt'] = Asset('binance', 'usdt', float(r['usdt']['free']), now)
        assets['binance:btc'] = Asset('binance', 'btc', float(r['btc']['free']), now)
        assets['binance:eth'] = Asset('binance', 'eth', float(r['eth']['free']), now)
        assets['binance:bch'] = Asset('binance', 'bch', float(r['bcc']['free']), now)
        assets['binance:xrp'] = Asset('binance', 'xrp', float(r['xrp']['free']), now)
        assets['binance:bnb'] = Asset('binance', 'bnb', float(r['bnb']['free']), now)

        self.logger.info('BALANCE_UPDATED: \n{}'.format(self._build_assets_text(assets)))
        self.last_updated = ts()
        break
      except Exception as e:
        gevent.sleep(2)
        retry_count += 1
    return assets

  def _build_assets_text(self, assets):
    texts = []
    sorted_keys = sorted(assets.keys(), key=lambda x: to_comparable_repr(x))
    for key in sorted_keys:
      asset = assets[key]
      texts.append('  {}'.format(ContentLines.get_balance_line(key, asset.volume)))
    return '\n'.join(texts)
