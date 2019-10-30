# -*- coding: utf-8 -*-
import logging
import logging.handlers

import yaml
from raven.handlers.logging import SentryHandler

from carbi.client.exchange.http.binance import BinanceClient, BinanceConfiguration
from carbi.client.exchange.http.bitfinex import BitfinexClient, BitfinexConfiguration
from carbi.client.exchange.http.cex import CexClient, CexConfiguration
from carbi.client.exchange.http.coinone import CoinoneClient, CoinoneConfiguration
from carbi.client.exchange.http.korbit import KorbitClient
from carbi.client.exchange.http.okex import OkexClient, OkexConfiguration
from carbi.client.exchange.http.poloniex import PoloniexClient, PoloniexConfiguration
from carbi.client.gcp.bigquery import BigQueryClient
from carbi.config import CarbiConfigKeys
from carbi.module.channel import ChannelProvider
from carbi.policy import ExchangePolicyProvider
from carbi.utils.dyprops import DynamicProperties


class Injector(DynamicProperties):
  @staticmethod
  def create(config_file_path):
    injector = Injector()
    install_config(injector, config_file_path)
    install_exchange_policies(injector)
    install_credentials(injector)
    install_client(injector)
    install_channels(injector)
    install_logger(injector)
    install_sentry_logger(injector)
    return injector


def install_config(injector, config_file_path):
  with open(config_file_path, 'r') as f:
    config = yaml.load(f)
    CarbiConfigKeys.validate(config)
    injector.config = config


def install_credentials(injector):
  injector.credentials = DynamicProperties(
    cex=CexConfiguration.load_from_file("conf/credentials/cex.json"),
    coinone=CoinoneConfiguration.load_from_file("conf/credentials/coinone.json"),
    poloniex=PoloniexConfiguration.load_from_file("conf/credentials/poloniex.json"),
    bitfinex=BitfinexConfiguration.load_from_file("conf/credentials/bitfinex.json"),
    binance=BinanceConfiguration.load_from_file("conf/credentials/binance.json"),
    okex=OkexConfiguration.load_from_file("conf/credentials/okex.json")
  )


def install_exchange_policies(injector):
  injector.exchange_policies = ExchangePolicyProvider(injector.config)


def install_client(injector):
  injector.cex_client = CexClient(injector.credentials.cex)
  injector.coinone_client = CoinoneClient(injector.credentials.coinone)
  injector.poloniex_client = PoloniexClient(injector.credentials.poloniex)
  injector.bitfinex_client = BitfinexClient(injector.credentials.bitfinex)
  injector.binance_client = BinanceClient(injector.credentials.binance)
  injector.korbit_client = KorbitClient()
  injector.okex_client = OkexClient(injector.credentials.okex)

  injector.bigquery_client = BigQueryClient('conf/credentials/google_service_account.json')


def install_channels(injector):
  injector.channels = ChannelProvider(injector)


def install_logger(injector):
  logger = logging.getLogger("carbi")
  logger.propagate = False
  logger.setLevel(logging.INFO)

  log_file_name = "logs/history.log"
  formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
  file_handler = logging.handlers.TimedRotatingFileHandler(filename=log_file_name, when='midnight')
  file_handler.setFormatter(formatter)
  console_handler = logging.StreamHandler()
  console_handler.setFormatter(formatter)
  logger.addHandler(console_handler)
  logger.addHandler(file_handler)

  injector.logger = logger


def install_sentry_logger(injector):
  if not injector.config[CarbiConfigKeys.SENTRY_ENABLED]:
    return
  # Sentry 설정이 되어 있는 경우에만 설정한다.
  sentry_address = injector.config[CarbiConfigKeys.SENTRY_ADDRESS]
  sentry_handler = SentryHandler(sentry_address)
  sentry_handler.setLevel(logging.ERROR)
  injector.logger.addHandler(sentry_handler)
