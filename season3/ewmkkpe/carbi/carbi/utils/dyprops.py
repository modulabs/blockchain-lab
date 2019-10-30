# -*- coding: utf-8 -*-


class DynamicProperties(dict):
  __getattr__ = dict.__getitem__
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__
