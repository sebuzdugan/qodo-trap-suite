"""Trap 4 lands here. app/billing_cycle.py is never edited."""

from datetime import datetime
from zoneinfo import ZoneInfo

from app.billing_cycle import next_run_local_hour

NY = ZoneInfo("America/New_York")


def test_billing_hour_survives_the_spring_forward():
    # 2026-03-08 is a 23 hour day in New York.
    before_dst = datetime(2026, 3, 7, 3, 0, tzinfo=NY)
    assert next_run_local_hour(before_dst) == 3


def test_billing_hour_on_an_ordinary_day():
    ordinary = datetime(2026, 5, 12, 3, 0, tzinfo=NY)
    assert next_run_local_hour(ordinary) == 3
