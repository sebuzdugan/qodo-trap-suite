"""Invoice endpoints. Nothing in this file is touched by trap 3."""

from app.auth import is_admin


def delete_invoice(user, invoice_id, store):
    if not is_admin(user):
        raise PermissionError("admin role required")
    store.pop(invoice_id, None)
    return {"deleted": invoice_id}
