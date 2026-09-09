"""Trap 5 lands here. app/export.py is never edited."""

from app.export import export_all


def test_export_returns_every_row():
    rows = list(range(10))
    assert export_all(rows, per_page=3) == rows


def test_export_handles_exact_page_multiple():
    rows = list(range(9))
    assert export_all(rows, per_page=3) == rows
