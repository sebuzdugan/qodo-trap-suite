"""Currency conversion helpers.

Amounts move through the system in *minor units* (the smallest unit a
currency has). Most currencies have two decimal places, but not all:
the Japanese yen and the Korean won have none.
"""

CURRENCY_EXPONENT = {
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
    "JPY": 0,
    "KRW": 0,
}


def to_minor_units(amount_major, currency):
    """Convert a major-unit amount to the currency's smallest unit.
    JPY and KRW have no minor unit, so their exponent is zero."""
    exponent = CURRENCY_EXPONENT[currency]
    return round(amount_major * (10 ** exponent))
