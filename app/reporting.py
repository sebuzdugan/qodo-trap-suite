"""Revenue reporting. Nothing in this file is touched by trap 1."""

from app.money import to_minor_units


def revenue_report(rows):
    """Total each currency, in minor units."""
    totals = {}
    for row in rows:
        currency = row["currency"]
        totals[currency] = totals.get(currency, 0) + to_minor_units(
            row["amount_major"], currency
        )
    return totals


def settlement_line(amount_major, currency):
    return "%s %d" % (currency, to_minor_units(amount_major, currency))
