# Use modern Python
from __future__ import unicode_literals, absolute_import, print_function

from django.db.models import Q

from .models import Permission


def has_permission(user_id, action_name, **parameter_values):
    """
    Verify if one user have permissions to perform the requested action with the given parameters
    :param user_id: User id
    :param action_name: string Permission name
    :param parameter_values: the grant parameter values
    :return: bool
    """
    permission = Permission.objects.get(code=action_name)

    if has_user_grant(user_id, permission, parameter_values):
        return True

    if has_group_grant(user_id, permission, parameter_values):
        return True

    return False


def has_user_grant(user_id, permission, parameter_values=None):
    """
    Verify if one user have the given permission through UserGrant
    """
    return permission.permission_user_grants.filter(
        user_id=user_id
    ).filter(
        Q(parameter_values=parameter_values) | Q(parameter_values={})
    ).exists()


def has_group_grant(user_id, permission, parameter_values=None):
    """
    Verify if one user have the given permission through GroupGrant
    """
    return permission.permission_group_grants.filter(
        group__user__id=user_id
    ).filter(
        Q(parameter_values=parameter_values) | Q(parameter_values={})
    ).exists()
