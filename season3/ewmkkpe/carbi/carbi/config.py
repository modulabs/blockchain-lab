# -*- coding: utf-8 -*-


class CarbiConfigKeys(object):
  TRADE_ENABLED = 'TRADE_ENABLED'
  LOOP_DELAY_MILLIS = 'LOOP_DELAY_MILLIS'
  PROFIT_MARGIN_THRESHOLD = 'PROFIT_MARGIN_THRESHOLD'

  SLACK_ENABLED = 'SLACK_ENABLED'

  SENTRY_ENABLED = 'SENTRY_ENABLED'
  SENTRY_ADDRESS = 'SENTRY_ADDRESS'

  GCLOUD_BIGQUERY_ENABLED = 'GCLOUD_BIGQUERY_ENABLED'

  BINANCE_BNB_FEE_DEDUCT_ENABLED = 'BINANCE_BNB_FEE_DEDUCT_ENABLED'

  BALANCER_TICK_MILLIS = 'BALANCER_TICK_MILLIS'
  BALANCER_TICK_PERIOD = 'BALANCER_TICK_PERIOD'

  COINONE_TAKER_FEE = 'COINONE_TAKER_FEE'
  CEX_TAKER_FEE = 'CEX_TAKER_FEE'
  BINANCE_TAKER_FEE = 'BINANCE_TAKER_FEE'
  KORBIT_TAKER_FEE = 'KORBIT_TAKER_FEE'

  def __init__(self):
    pass

  @staticmethod
  def validate(config):
    required_keys = [
      CarbiConfigKeys.TRADE_ENABLED,
      CarbiConfigKeys.LOOP_DELAY_MILLIS,
      CarbiConfigKeys.PROFIT_MARGIN_THRESHOLD,
      CarbiConfigKeys.SLACK_ENABLED,
      CarbiConfigKeys.SENTRY_ENABLED,
      CarbiConfigKeys.SENTRY_ADDRESS,
      CarbiConfigKeys.GCLOUD_BIGQUERY_ENABLED,
      CarbiConfigKeys.BINANCE_BNB_FEE_DEDUCT_ENABLED,
      CarbiConfigKeys.BALANCER_TICK_MILLIS,
      CarbiConfigKeys.BALANCER_TICK_PERIOD,
      CarbiConfigKeys.COINONE_TAKER_FEE,
      CarbiConfigKeys.CEX_TAKER_FEE,
      CarbiConfigKeys.BINANCE_TAKER_FEE,
      CarbiConfigKeys.KORBIT_TAKER_FEE,
    ]
    for required_key in required_keys:
      assert required_key in config, 'CONFIG_ERROR: {} is required key.'.format(required_key)
