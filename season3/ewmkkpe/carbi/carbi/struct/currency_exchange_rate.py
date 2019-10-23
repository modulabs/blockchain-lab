# -*- coding: utf-8 -*-
from carbi.utils import ts


class CurrencyExchangeRate(object):
  def __init__(self, equity_pair, rate, timestamp):
    # 일반적인 환율의 EquityPair와 반대이다.
    # 다른 EquityPair와 의미를 똑같이 하기 위함이다.
    # 환율: USD/KRW (USD로 KRW를 살때의 환율)
    # 다른것: ETH/KRW (BTC로 ETH를 사는 것을 의미)
    # 의미를 동일하게 가져가기 위해 KRW/USD로 표기합니다.
    self.equity_pair = equity_pair
    self.rate = rate
    self.timestamp = timestamp

  @property
  def symbol(self):
    # KRW/USD로 표기되므로 앞에있는거 리턴한다.
    return self.equity_pair.split('/')[0]

  def to_bigquery_struct(self, snapshot_ts):
    return dict(
      symbol=self.symbol,
      equity_pair=self.equity_pair,
      rate=self.rate,
      ts=self.timestamp / 1000,
      snapshot_ts=snapshot_ts,
      created=ts() / 1000,
    )

  def __str__(self):
    return "CurrencyExchangeRate(%s, %s)" % (self.equity_pair, self.rate)

  def __repr__(self):
    return self.__str__()
