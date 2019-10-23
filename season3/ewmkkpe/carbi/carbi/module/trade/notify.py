# -*- coding: utf-8 -*-
import sys

from datetime import datetime
from carbi.config import CarbiConfigKeys
from carbi.module.trade.notifier import notify_slack
from carbi.module.trade.notifier.content.notify_trade_execution_result import NotifyTradeExecutionResultMessageContent
from carbi.module.trade.notifier.content.notify_trasfer_needed import NotifyTransferNeededMessageContent
from carbi.module.trade.notifier.content.notify_balancing_task_result import NotifyBalancingTaskResultMessageContent
from carbi.module.trade.notifier.content.notify_balance_status import NotifyBalanceStatusMessageContent
from carbi.utils.dyprops import DynamicProperties

SLACK_URLS = DynamicProperties(
  ALARM_URL='https://hooks.slack.com/services/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',
  STATUS_URL='https://hooks.slack.com/services/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',
  TX_URL='https://hooks.slack.com/services/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',
)


class TradeNotifier(object):
  def __init__(self, injector):
    self.injector = injector
    self.logger = injector.logger
    self.last_sent_balance_status = None

  def notify_result(self, result):
    """
    거래 결과 및 거래로 인해 코인 송금이 필요한 경우 슬랙으로 알린다.
    """
    if not self.injector.config[CarbiConfigKeys.SLACK_ENABLED]:
      return
    self._notify_trade_execution_result(result)
    self._notify_trade_execution_error(result)
    self._notify_transfer_needed(result)

  def _notify_trade_execution_result(self, result):
    try:
      url = SLACK_URLS.TX_URL
      content = NotifyTradeExecutionResultMessageContent(result)
      notify_slack(url, content)
    except Exception as e:
      self.logger.error(e, exc_info=sys.exc_info())

  def _notify_trade_execution_error(self, result):
    if result.is_trade_execution_succeed:
      return
    try:
      url = SLACK_URLS.ALARM_URL
      content = NotifyTradeExecutionResultMessageContent(result)
      notify_slack(url, content)
    except Exception as e:
      self.logger.error(e, exc_info=sys.exc_info())

  def _notify_transfer_needed(self, result):
    if not result.is_transfer_needed:
      return
    try:
      url = SLACK_URLS.ALARM_URL
      content = NotifyTransferNeededMessageContent(result)
      notify_slack(url, content)
    except Exception as e:
      self.logger.error(e, exc_info=sys.exc_info())

  def notify_balancing_task_result(self, result, balancing_task):
    """
    거래로 인해 생기는 코인 갯수 오차 등을 보정한 경과를 슬랙으로 알린다.
    """
    if not self.injector.config[CarbiConfigKeys.SLACK_ENABLED]:
      return
    try:
      url = SLACK_URLS.ALARM_URL
      content = NotifyBalancingTaskResultMessageContent(result, balancing_task)
      notify_slack(url, content)
    except Exception as e:
      self.logger.error(e, exc_info=sys.exc_info())

  def notify_balance_status(self, market_ctx, balance_ctx):
    """
    주기적으로 현재 펀드의 잔액에 대한 정보를 슬랙으로 알린다.
    """
    if not self._should_notify_balance_status():
      return
    try:
      url = SLACK_URLS.STATUS_URL
      content = NotifyBalanceStatusMessageContent(market_ctx, balance_ctx)
      notify_slack(url, content)
      self.last_sent_balance_status = datetime.now()
    except Exception as e:
      self.logger.error(e, exc_info=sys.exc_info())

  def _should_notify_balance_status(self):
    if not self.injector.config[CarbiConfigKeys.SLACK_ENABLED]:
      return False
    now = datetime.now()
    if not self.last_sent_balance_status:
      return True
    if self._equal_in_minute_scale(self.last_sent_balance_status, now):
      return False
    if now.minute % 60 == 0:
      return True
    return False

  def _equal_in_minute_scale(self, dt1, dt2):
    """
    dt1과 dt2가 year, month, day, hour, minute 값이 같을 경우 True를 return 한다.
    :param dt1: datetime.datetime
    :param dt2: datetime.datetime
    :return:
    """
    return dt1.year == dt2.year and dt1.month == dt2.month and dt1.day == dt2.day and dt1.hour == dt2.hour \
           and dt1.minute == dt2.minute
