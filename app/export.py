"""Bulk export. Nothing in this file is touched by trap 5."""

from app.paging import page_bounds


def export_all(rows, per_page=3):
    """Walk every page and return every row, in order."""
    out = []
    page = 1
    while True:
        start, end = page_bounds(page, per_page)
        chunk = rows[start:end]
        if not chunk:
            break
        out.extend(chunk)
        page += 1
    return out
