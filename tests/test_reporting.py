"""Trap 1 lands here. Nothing in this test's target file is edited."""

from app.reporting import revenue_report, settlement_line


def test_zero_decimal_currency_is_not_scaled():
    rows = [{"amount_major": 1000, "currency": "JPY"}]
    assert revenue_report(rows) == {"JPY": 1000}


def test_two_decimal_currency_still_scales():
    rows = [{"amount_major": 10, "currency": "USD"}]
    assert revenue_report(rows) == {"USD": 1000}


def test_settlement_line_for_yen():
    assert settlement_line(1000, "JPY") == "JPY 1000"
