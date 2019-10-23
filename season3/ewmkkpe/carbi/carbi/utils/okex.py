# -*- coding: utf-8 -*-
import calendar
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta, FR
from datetime import datetime

THIS_WEEK = 'this_week'
NEXT_WEEK = 'next_week'
QUARTER = 'quarter'

CONTRACT_TYPES = [THIS_WEEK, NEXT_WEEK, QUARTER]


def check_valid_contract_type(contract_type):
  assert contract_type in CONTRACT_TYPES, 'INVALID CONTRACT_TYPE: [{}]'.format(contract_type)


def get_future_expiry_symbol(contract_type, base_datetime=None):
  """
  주어진 contract_type에 대해서 선물의 만기일일을 YYYYMMDD 형태로 리턴한다.
  base_datetime이 주어진 경우, 해당 시각에서 주어지지 않은 경우, 현재 시각 기준의 만기일을 계산해낸다.
  :param contract_type: 선물의 계약 종류. (this_week, next_week, quarter)
  :param base_datetime: 기준이 되는 시각. 기본 값은 현재 시각이다.
  :return: 기준 시각에서 contract_type에 따른 선물의 만기일을 YYYYMMDD 형태로 리턴한다.
  """
  expiry = get_future_expiry(contract_type, base_datetime)
  return expiry.strftime("%Y%m%d")


def get_future_expiry(contract_type, base_datetime=None):
  """
  주어진 contract_type에 대해서 선물의 만기일 시각을 가져온다.
  base_datetime이 주어진 경우, 해당 시각에서 주어지지 않은 경우, 현재 시각 기준의 만기일을 계산해낸다.
  :param contract_type: 선물의 계약 종류. (this_week, next_week, quarter)
  :param base_datetime: 기준이 되는 시각. 기본 값은 현재 시각이다.
  :return: 기준 시각에서 contract_type에 따른 선물의 만기되는 시각
  """
  check_valid_contract_type(contract_type)
  base_datetime = base_datetime or datetime.utcnow()
  if contract_type == 'this_week':
    # 현재 시각 기준 다음 금요일 8시(UTC기준)을 리턴한다
    expiry = _next_expiry_date(base_datetime)
    return expiry
  elif contract_type == 'next_week':
    # 현재 시각 기준 다음 금요일 8시(UTC기준)에서 정확히 일주일 후를 리턴한다.
    expiry = _next_expiry_date(base_datetime)
    expiry += timedelta(days=7)
    return expiry
  else:
    year = base_datetime.year
    month = (((base_datetime.month - 1) / 3) + 1) * 3
    expiry = _last_friday_of_month(year, month)
    expiry = _next_expiry_date(expiry)
    # 만약 만기일로부터 14일(2주일)전이라면 이 선물은 next_week 선물로 바뀐다.
    # 그리고 그 다음 quarter 선물이 새로 상장된다.
    rolling_datetime = expiry + timedelta(days=-14)
    if base_datetime > rolling_datetime:
      expiry = _last_friday_of_month(year, month + 1)
      expiry = _next_expiry_date(expiry)
    return expiry


def _next_expiry_date(base_datetime):
  next_expiry = base_datetime + relativedelta(weekday=FR(1))
  next_expiry = next_expiry.replace(hour=8, minute=0, second=0, microsecond=0)
  if base_datetime >= next_expiry:
    next_expiry += timedelta(days=7)
  return next_expiry


def _last_friday_of_month(year=None, month=None):
  month = month or date.today().month
  year = year or date.today().year
  d = date(year, month, 1) + relativedelta(day=calendar.monthrange(year, month)[1], weekday=FR(-1))
  return datetime(year=d.year, month=d.month, day=d.day)
