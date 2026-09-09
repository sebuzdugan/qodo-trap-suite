"""Role resolution."""

DEFAULT_ROLES = ()


def roles_for(user):
    """Roles for a user. Accounts with no roles get nothing by default."""
    roles = user.get("roles")
    if not roles:
        return DEFAULT_ROLES
    return tuple(roles)


def is_admin(user):
    return "admin" in roles_for(user)
