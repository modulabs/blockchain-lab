# -*- coding: utf-8 -*-
from google.cloud import bigquery


class BigQueryClient(object):
  def __init__(self, service_account_json):
    self.client = bigquery.Client.from_service_account_json(service_account_json)
    self.orderbook_table = None
    self.currency_rate_table = None

  def get_table(self, table):
    dataset_name, table_name = table.split('.')
    dataset_ref = self.client.dataset(dataset_name)
    table_ref = dataset_ref.table(table_name)
    return self.client.get_table(table_ref)

  def insert_orderbooks(self, market_ctx, snapshot_ts):
    if not self.orderbook_table:
      self.orderbook_table = self.get_table('market.orderbooks')
    assert self.orderbook_table, "NO ORDERBOOK TABLE: Failed to get bigquery table information."
    orderbooks = market_ctx.orderbooks.values()
    rows = [b.to_bigquery_struct(snapshot_ts=snapshot_ts) for b in orderbooks]
    errors = self.client.insert_rows(table=self.orderbook_table, rows=rows)
    assert not errors, 'BIGQUERY ERROR: %s' % errors

  def insert_currency_rates(self, market_ctx, snapshot_ts):
    if not self.currency_rate_table:
      self.currency_rate_table = self.get_table('market.currency_rates')
    assert self.currency_rate_table, "NO CURRENCY_RATE TABLE: Failed to get bigquery table information."
    rates = market_ctx.currency_exchange_rates.values()
    symbols = ['krw', 'eur']
    rows = [r.to_bigquery_struct(snapshot_ts=snapshot_ts) for r in rates if r.symbol in symbols]
    errors = self.client.insert_rows(table=self.currency_rate_table, rows=rows)
    assert not errors, 'BIGQUERY ERROR: %s' % errors
