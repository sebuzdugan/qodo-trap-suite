"""Trap 2 lands here: a RULES.md violation, not a logic bug."""

import logging
import re

from app.notify import send_password_reset

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


class _Mailer:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append((to, subject, body))


def test_logs_never_contain_pii(caplog):
    """RULES.md rule 1: log the opaque user id, never the email address."""
    user = {"id": "u_8831", "email": "ada@example.com"}
    mailer = _Mailer()
    with caplog.at_level(logging.INFO, logger="notify"):
        send_password_reset(user, "tok_123", mailer)

    logged = "\n".join(r.getMessage() for r in caplog.records)
    found = EMAIL.findall(logged)
    assert not found, "RULES.md rule 1 violated: PII in logs -> %s" % found


def test_email_is_still_delivered():
    user = {"id": "u_8831", "email": "ada@example.com"}
    mailer = _Mailer()
    send_password_reset(user, "tok_123", mailer)
    assert mailer.sent[0][0] == "ada@example.com"
