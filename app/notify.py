"""Outbound notifications."""

import logging

log = logging.getLogger("notify")


def send_password_reset(user, token, mailer):
    """Mail a password reset link.

    See RULES.md rule 1: log the opaque user id, never the email address.
    """
    log.info("password reset requested user_id=%s", user["id"])
    mailer.send(
        to=user["email"],
        subject="Reset your password",
        body="token=%s" % token,
    )
    return True
