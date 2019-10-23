# -*- coding: utf-8 -*-
import sys


class Trade:
  def __init__(self, base, target, ratio, fee):
    # base.qty * ratio * (1-fee) => target.qty
    # target.qty / ratio / (1-fee) => base.qty
    self.base = base
    self.target = target
    self.ratio = ratio
    self.fee = fee

  def calculate_target_qty(self, base_qty):
    return base_qty * self.ratio * (1 - self.fee)

  def calculate_base_qty(self, target_qty):
    return target_qty / self.ratio / (1 - self.fee)


class Asset:
  def __init__(self, name):
    self.name = name
    self.qty = sys.maxint
    self.next_trade = None
    self.prev_trade = None

  def add_next(self, target_asset, ratio, fee):
    trade = Trade(self, target_asset, ratio, fee)
    self.next_trade = trade
    target_asset.prev_trade = trade

  def add_prev(self, base_asset, ratio, fee):
    trade = Trade(base_asset, self, ratio, fee)
    self.prev_trade = trade
    base_asset.next_trade = trade

  def set_qty(self, qty, depth=0):
    # 소수 반올림에 의한 무한루프를 방지하기 위해서 이미 있는 값에서 1/100,000 이상 작아져야지만 값의 변화가 propagate 되도록 수정함
    # if qty < self.qty and abs(qty - self.qty) > 0.00001:
    # if qty < self.qty and qty / self.qty < 1.0 - 1e-12:
    if qty < self.qty and depth < 40:
      self.qty = qty

      if self.next_trade is not None:
        next_qty = self.next_trade.calculate_target_qty(qty)
        self.next_trade.target.set_qty(next_qty, depth + 1)
      if self.prev_trade is not None:
        prev_qty = self.prev_trade.calculate_base_qty(qty)
        self.prev_trade.base.set_qty(prev_qty, depth + 1)

  def __repr__(self):
    if self.next_trade is not None:
      return "Asset[{} : {}] -> {}".format(self.name, self.qty, self.next_trade.target)
    else:
      return "Asset[{} : {}]]".format(self.name, self.qty)
