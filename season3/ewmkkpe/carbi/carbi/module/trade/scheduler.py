# -*- coding: utf-8 -*-


def schedule_tasks(all_tasks):
  """
  그룹핑된 Task는 순차적으로 실행된다.
  """

  def _group_key(t):
    exchange = t.chain_node.exchange
    target_equity = t.chain_node.target_equity
    base_equity = t.chain_node.base_equity
    action = t.chain_node.action
    return '{}.{}.{}.{}'.format(exchange, target_equity, base_equity, action)

  grouped_tasks = {}
  for task in all_tasks:
    group_key = _group_key(task)
    if group_key not in grouped_tasks:
      grouped_tasks[group_key] = []
    tasks = grouped_tasks[group_key]
    tasks.append(task)
  return grouped_tasks
