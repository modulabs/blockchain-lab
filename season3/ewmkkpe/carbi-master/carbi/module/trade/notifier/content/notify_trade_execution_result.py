# -*- coding: utf-8 -*-
from carbi.utils.lines import ContentLines
from carbi.utils import datetime_kst, datetime_utc


class NotifyTradeExecutionResultMessageContent(object):
  def __init__(self, result):
    self.result = result

  @property
  def title(self):
    is_succeed = self.result.is_trade_execution_succeed
    return '다음 거래가 성공적으로 실행되었습니다.' if is_succeed else '다음 거래를 실행하다가 실패하였습니다.'

  @property
  def text(self):
    return self._build_text()

  def _build_text(self):
    balance_dirty_marker = '' if self.result.is_balance_updated_correctly else '(*)'
    trade_succeed_marker = '' if self.result.is_trade_execution_succeed else '(*)'
    texts = [
      "{}".format(self.result.graph),
      "",
      "Trade Executions {}".format(trade_succeed_marker),
      "",
      "{}".format(self._build_task_text(self.result)),
      "",
      "Asset Changes {}".format(balance_dirty_marker),
      "",
      "{}".format(self._build_balance_changes_text()),
      "",
      "{}".format(self._build_total_balance_changes_text()),
      "",
      "Profit: {0:,.0f} KRW".format(self.result.total_profit),
      "Est.Profit: {0:,.0f} KRW".format(self._build_estimated_profit()),
      "Est.Profit Margin: {0:.3f} %".format(self.result.graph.total_profit_margin() * 100),
      "KRW/USD: {}".format(self.result.market_ctx.usd_krw_price),
      "",
      "Time(UTC) : {}".format(datetime_utc()),
      "Time(KST) : {}".format(datetime_kst()),
    ]
    return "\n".join(texts)

  def _build_task_text(self, result):
    texts = []
    for task in result.tasks:
      chain_node = task.chain_node
      line = '{0}: {1} @ {2} [{3}]'.format(chain_node, task.volume, task.price, task.status)
      texts.append(line)
      if task.error:
        texts.append('  * {}'.format(format(task.error)))
    return '\n'.join(texts)

  def _build_balance_changes_text(self):
    texts = [self._build_balance_change_line(change) for change in self.result.balance_changes]
    return '\n'.join(texts)

  def _build_total_balance_changes_text(self):
    texts = [self._build_balance_change_line(change) for change in self.result.total_balance_changes]
    return '\n'.join(texts)

  def _build_balance_change_line(self, change):
    equity = change.equity
    volume = change.volume
    diff = change.diff
    return ContentLines.get_balance_line(equity, volume, diff)

  def _is_usd_profit_graph(self):
    first_base_equity = self.result.graph.chain.first_base_equity
    return first_base_equity in ['usd' or 'usdt']

  def _build_estimated_profit(self):
    estimated_profit = self.result.graph.total_profit()
    if self._is_usd_profit_graph():
      estimated_profit *= self.result.market_ctx.usd_krw_price
    return estimated_profit
