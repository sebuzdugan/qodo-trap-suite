"""Trap 3 lands here. app/api_invoices.py is never edited."""

import pytest

from app.api_invoices import delete_invoice


def test_legacy_user_without_roles_is_not_an_admin():
    legacy_user = {"id": "u_0001"}  # predates the roles table
    store = {"inv_1": {"total": 100}}
    with pytest.raises(PermissionError):
        delete_invoice(legacy_user, "inv_1", store)
    assert "inv_1" in store


def test_real_admin_can_delete():
    admin = {"id": "u_0002", "roles": ["admin"]}
    store = {"inv_1": {"total": 100}}
    assert delete_invoice(admin, "inv_1", store) == {"deleted": "inv_1"}
