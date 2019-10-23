# -*- coding: utf-8 -*-

from carbi.utils import ts


class NonceIssuer(object):
  def __init__(self):
    self._last_ts = ts()

  def next_nonce(self):
    new_ts = ts()
    if new_ts <= self._last_ts:
      new_ts = self._last_ts + 1
    self._last_ts = new_ts
    return new_ts
