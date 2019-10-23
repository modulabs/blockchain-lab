# -*- coding: utf-8 -*-
import sys

from carbi.config import CarbiConfigKeys
from carbi.utils import ts


class BigQueryStreamer(object):
  def __init__(self, injector):
    self.injector = injector
    self.logger = injector.logger
    self.client = injector.bigquery_client

  def handle(self, market_ctx):
    if not self.injector.config[CarbiConfigKeys.GCLOUD_BIGQUERY_ENABLED]:
      return
    snapshot_ts = ts() / 1000
    try:
      self.client.insert_orderbooks(market_ctx, snapshot_ts)
      self.logger.info('INSERT ORDERBOOK OK.')
    except Exception as e:
      self.logger.error(e, exc_info=sys.exc_info())
    try:
      self.client.insert_currency_rates(market_ctx, snapshot_ts)
      self.logger.info('INSERT CURRENCY_RATE OK.')
    except Exception as e:
      self.logger.error(e, exc_info=sys.exc_info())
