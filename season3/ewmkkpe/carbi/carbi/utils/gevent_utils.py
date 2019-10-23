# -*- coding: utf-8 -*-
import sys

from gevent.event import AsyncResult
from gevent.pool import Pool

import gevent


def gevent_call_async(func, *args, **kwargs):
  result = AsyncResult()

  def wrapped(*args, **kwargs):
    try:
      result.set(func(*args, **kwargs))
    except Exception as e:
      result.set_exception(e, exc_info=sys.exc_info())

  gevent.spawn(wrapped, *args, **kwargs)
  return result


def gevent_call_async_with_pool(pool, func, *args, **kwargs):
  result = AsyncResult()

  def wrapped(*args, **kwargs):
    try:
      result.set(func(*args, **kwargs))
    except Exception as e:
      result.set_exception(e, exc_info=sys.exc_info())

  pool.spawn(wrapped, *args, **kwargs)
  return result


def gevent_map_async(func, sequence, pool=None, pool_size=None):
  """
  apply python map function on sequence with gevent_call of func.
  Each func operation will be runned concurrently by gevent.
  Non-Blocking method.
  :param func: should be form of return value = func(single element of sequence)
  :param sequence:
  :param pool:
  :param pool_size:
  :return: return list of async
  """
  if pool is None:
    if pool_size is None:
      return map(lambda elem: gevent_call_async(func, elem), sequence)
    else:
      assert pool_size > 0, 'pool size must be bigger than 0.'
      pool = gevent.pool.Pool(pool_size)

  return map(lambda elem: gevent_call_async_with_pool(pool, func, elem), sequence)


def gevent_map(func, sequence, pool=None, pool_size=None):
  """
  apply python map function on sequence with gevent_call of func.
  Each func operation will be run concurrently by gevent.
  Could raise Exception if exception occurred during apply func method.
  Blocking method.
  :param func: should be form of return value = func(single element of sequence)
  :param sequence:
  :param pool:
  :param pool_size:
  :return: return list of return value of func
  """
  return [async.get() for async in gevent_map_async(func, sequence, pool, pool_size)]


def gevent_filter(func, sequence, pool=None, pool_size=None):
  """
  apply python filter function on sequence with gevent_call of func.
  Each func operation will be run concurrently by gevent.
  Could raise Exception if exception occurred during apply func method.
  Blocking method.
  :param func: should be form of boolean = func(single element of sequence)
  :param sequence:
  :param pool:
  :param pool_size:
  :return:
  """
  filter_results = gevent_map(func, sequence, pool, pool_size)  # blocking process, return list of boolean
  result = []
  for filter_result, elem in zip(filter_results, sequence):
    if filter_result:
      result.append(elem)
  return result
