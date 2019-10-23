# -*- coding: utf-8 -*-
from functools import wraps


def public(func):
  """
  거래소의 Public API임을 나타내는 데코레이터.
  다른 기능은 전혀 없다.
  """

  @wraps(func)
  def wrapped(*args, **kwargs):
    return func(*args, **kwargs)

  return wrapped


def private(func):
  """
  거래소의 Private API임을 나타내는 데코레이터.
  다른 기능은 전혀 없다.
  """

  @wraps(func)
  def wrapped(*args, **kwargs):
    return func(*args, **kwargs)

  return wrapped


def callback(func):
  """
  콜백 메서드임을 나타내는 데코레이터.
  다른 기능은 전혀 없다.
  """

  @wraps(func)
  def wrapped(*args, **kwargs):
    return func(*args, **kwargs)

  return wrapped


def validate_response(response, required_keys):
  for required_key in required_keys:
    if required_key not in response:
      raise Exception('INVALID_RESPONSE: missing required key in response: {}'.format(required_key))
