"""Pagination helpers."""


def page_bounds(page, per_page):
    """Half-open slice bounds (start, end) for a 1-based page number."""
    start = (page - 1) * per_page
    return start, start + per_page
