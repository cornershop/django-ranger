# Use modern Python
from __future__ import unicode_literals, absolute_import, print_function
import hashlib
import json

from django.db.models import Q

from .models import Permission


class PermissionManager(object):

    def __init__(self, user):
        self.data = []
        self.user_grants = user.permission_user_grants.select_related('permission').all()
        self.group_grants = user.permission_group_grants.select_related('permission').all()

        self.set_grant_hashes(self.user_grants)
        self.set_grant_hashes(self.group_grants)
        self.data = list(set(self.data))

    def set_grant_hashes(self, grants):
        for grant in grants:
            hash_code = self.get_hash(grant.permission.code, grant.parameter_values)
            self.data.append(hash_code)

    @staticmethod
    def get_hash(permission_code, parameter_values):
        parameters_string = json.dumps(parameter_values, sort_keys=True)
        string_code = "{}-{}".format(permission_code, parameters_string)
        hash_code = hashlib.sha256(string_code)
        return hash_code

    def has_permission(self, action_name, **parameter_values):
        hash_code = self.get_hash(action_name, parameter_values)
        return hash_code in self.data


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
