# -*- coding: utf-8 -*-
import datetime
import math
import time

import pytz
from blist import sorteddict, sortedlist


def ts():
  """
  epoch timestamp를 return 합니다.
  :return:
  """
  return int(time.time() * 1000)


class TimeWindowedPercentileTracker:
  def __init__(self, time_window):
    """
    :param time_window: time in milliseconds
    """
    self.time_window = time_window
    self.ts_to_values = sorteddict()
    self.values = sortedlist()

  def add(self, ts, value):
    """
    :param ts: time in milliseconds
    :param value:
    :return:
    """
    self.ts_to_values[ts] = value
    self.values.add(value)

    for old_ts in self.ts_to_values.keys():
      if old_ts + self.time_window < ts:
        # discard this value
        old_value = self.ts_to_values[old_ts]
        del self.ts_to_values[old_ts]
        self.values.discard(old_value)
      else:
        break

  def get_percentile(self, percentile):
    """
    :param percentile: 0 means lowest value, 1 means highest value
    :return:
    """
    assert 0 <= percentile <= 1, 'percentile should be between 0 and 1'
    values = self.values
    return values[int(max(len(values) * percentile - 1, 0))]


def year_month_date():
  return datetime.datetime.utcnow().strftime("%Y-%m-%d")


def datetime_utc():
  return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def datetime_kst():
  return datetime.datetime.now(tz=pytz.timezone("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")


def similar(expected, actual, margin_of_error=1e-4):
  if expected == 0:
    return True

  if abs(actual / expected - 1) <= margin_of_error:
    return True
  return False


def check_floor_error_value(qty, floored_qty):
  if qty <= 0:
    return False

  floored_error = qty - floored_qty
  if floored_error / qty >= 0.01:
    return False
  return True


def geographical_interpolate(x, y, weight_x, weight_y):
  """
  x와 y의 기하평균으로 중간점을 정하는데, 각각의 weight를 정할 수 있습니다.
  :param x:
  :param y:
  :param weight_x:
  :param weight_y:
  :return:
  """
  assert x > 0, 'x should be bigger than 0.'
  assert y > 0, 'y should be bigger than 0.'
  assert weight_x >= 0, 'weight_x should be bigger than 0.'
  assert weight_y >= 0, 'weight_y should be bigger than 0.'

  weight_total = float(weight_x + weight_y)
  normalized_weight_x = weight_x / weight_total
  normalized_weight_y = weight_y / weight_total

  return math.pow(x, normalized_weight_x) * math.pow(y, normalized_weight_y)


class LimitedQueue(object):
  def __init__(self, limit):
    self.limit = limit
    self.q = []

  def insert(self, value):
    self.q.insert(0, value)

    while len(self.q) > self.limit:
      self.q.pop()

  def __iter__(self):
    return self.q.__iter__()

  def __len__(self):
    return self.q.__len__()

  def __repr__(self):
    return self.q.__repr__()

  def __getitem__(self, index):
    return self.q[index]

  def clear(self):
    self.q = []
