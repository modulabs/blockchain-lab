# -*- coding: utf-8 -*-
from carbi.utils.lines import ContentLines
from carbi.utils import datetime_kst, datetime_utc


class NotifyBalancingTaskResultMessageContent(object):
  def __init__(self, result, balancing_task):
    self.result = result
    self.equity = balancing_task.rule.equity
    self.target_volume = balancing_task.rule.balancing_task_target_volume

  @property
  def title(self):
    is_succeed = self.result.is_trade_execution_succeed
    return '다음 밸런싱이 성공적으로 실행되었습니다.' if is_succeed else '다음 밸런싱을 실행하다가 실패하였습니다.'

  @property
  def text(self):
    return self._build_text()

  def _build_text(self):
    balance_dirty_marker = '' if self.result.is_balance_updated_correctly else '(*)'
    trade_succeed_marker = '' if self.result.is_trade_execution_succeed else '(*)'
    usd_krw_price = self.result.market_ctx.usd_krw_price
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
      "Actual Volume: {0:.6f} {1}".format(self.result.total_symbol_balance(self.equity), self.equity),
      "Target Volume: {0:.6f} {1}".format(self.target_volume, self.equity),
      "KRW/USD: {0:.2f}".format(usd_krw_price),
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

  def _build_balance_change_line(self, change):
    equity = change.equity
    volume = change.volume
    diff = change.diff
    return ContentLines.get_balance_line(equity, volume, diff)
