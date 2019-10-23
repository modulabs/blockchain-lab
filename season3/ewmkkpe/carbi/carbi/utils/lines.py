# -*- coding: utf-8 -*-


class ContentLines(object):
  @staticmethod
  def get_balance_line(equity, volume, diff=0, is_marker_needed=False):
    if diff == 0:
      return ContentLines._get_balance_line_without_diff(equity, volume, is_marker_needed)
    marker = '(*)' if is_marker_needed else ''
    if 'krw' in equity:
      line = '{0:12}: {1:,.0f} ({2:+,.0f}) {3}'.format(equity, volume, diff, marker)
    elif 'usd' in equity:
      line = '{0:12}: {1:,.2f} ({2:+,.2f}) {3}'.format(equity, volume, diff, marker)
    elif 'usdt' in equity:
      line = '{0:12}: {1:,.2f} ({2:+,.2f}) {3}'.format(equity, volume, diff, marker)
    elif 'btc' in equity:
      line = '{0:12}: {1:,.5f} ({2:+,.5f}) {3}'.format(equity, volume, diff, marker)
    else:
      line = '{0:12}: {1:,.3f} ({2:+,.3f}) {3}'.format(equity, volume, diff, marker)
    return line.strip()

  @staticmethod
  def _get_balance_line_without_diff(equity, volume, is_marker_needed=False):
    marker = '(*)' if is_marker_needed else ''
    if 'krw' in equity:
      line = '{0:12}: {1:,.0f} {2}'.format(equity, volume, marker)
    elif 'usd' in equity:
      line = '{0:12}: {1:,.2f} {2}'.format(equity, volume, marker)
    elif 'usdt' in equity:
      line = '{0:12}: {1:,.2f} {2}'.format(equity, volume, marker)
    elif 'btc' in equity:
      line = '{0:12}: {1:,.5f} {2}'.format(equity, volume, marker)
    else:
      line = '{0:12}: {1:,.3f} {2}'.format(equity, volume, marker)
    return line.strip()
