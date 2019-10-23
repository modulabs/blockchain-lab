# -*- coding: utf-8 -*-
import random
import string


def random_srv_id():
  return str(random.randint(0, 1000))


def random_conn_id():
  letters = string.ascii_lowercase + string.digits
  return ''.join(random.choice(letters) for c in range(8))
