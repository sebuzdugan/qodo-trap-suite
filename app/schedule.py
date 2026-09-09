"""Scheduling helpers."""

from datetime import datetime, timedelta


def next_day_same_local_time(dt):
    """The same wall-clock time on the following calendar day.

    Wall-clock arithmetic on purpose: on a daylight-saving boundary a
    calendar day is 23 or 25 hours long, not 24.
    """
    naive_next = dt.replace(tzinfo=None) + timedelta(days=1)
    return naive_next.replace(tzinfo=dt.tzinfo)
