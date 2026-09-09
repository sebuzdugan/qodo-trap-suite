"""Billing cycle. Nothing in this file is touched by trap 4."""

from app.schedule import next_day_same_local_time


def next_run(dt):
    return next_day_same_local_time(dt)


def next_run_local_hour(dt):
    return next_run(dt).hour
