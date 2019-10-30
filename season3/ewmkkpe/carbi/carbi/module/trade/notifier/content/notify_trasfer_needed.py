# -*- coding: utf-8 -*-
from carbi.utils.lines import ContentLines
from carbi.utils import datetime_kst, datetime_utc


class NotifyTransferNeededMessageContent(object):
  def __init__(self, result):
    self.result = result

  @property
  def title(self):
    return '이 거래로 인해 송금해야할 코인이 있습니다.'

  @property
  def text(self):
    return self._build_text()

  def _build_text(self):
    texts = [
      "Asset Changes",
      "",
      "{}".format(self._build_balance_changes_text()),
      "",
      "{}".format(self._build_total_balance_changes_text()),
      "",
      "Time(UTC) : {}".format(datetime_utc()),
      "Time(KST) : {}".format(datetime_kst()),
    ]
    return "\n".join(texts)

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
    is_transfer_needed = change.is_transfer_needed
    return ContentLines.get_balance_line(equity, volume, diff, is_transfer_needed)
