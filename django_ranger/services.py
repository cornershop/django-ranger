# Use modern Python
from __future__ import unicode_literals, absolute_import, print_function
import hashlib
import json

from django.db.models import Q

from .models import Permission, GroupGrant


class PermissionManager(object):
    """
    This class allows managing user permissions.

    It is instantiated with a user instance and enlists all their permissions
     grants to achieve a better performance in multiple permission verifications.
    """

    def __init__(self, user):
        self.data = []
        self.user_grants = user.user_grants.select_related('permission').all()
        group_list = list(user.groups.all())
        self.group_grants = GroupGrant.objects.filter(group__in=group_list).select_related('permission').all()

        self.set_grant_hashes(self.user_grants)
        self.set_grant_hashes(self.group_grants)
        self.data = list(set(self.data))

    def set_grant_hashes(self, grants):
        """
        store the given grants into a hashes list.
        """
        for grant in grants:
            hash_code = self.get_hash(grant.permission.code, grant.parameter_values)
            self.data.append(hash_code)

    @staticmethod
    def get_hash(permission_code, parameter_values):
        """
        It's return a hash of the permission and their parameters.
        """
        parameters_string = json.dumps(parameter_values, sort_keys=True)
        string_code = "{}-{}".format(permission_code, parameters_string)
        hash_code = hashlib.sha256(string_code)
        return hash_code.hexdigest()

    def has_permission(self, action_name, **parameter_values):
        """
        Verifies if the instantiated user has the given permission with
        the given parameters.
        """
        hash_code = self.get_hash(action_name, parameter_values)
        if hash_code in self.data:
            return True

        hash_code = self.get_hash(action_name, {})
        if hash_code in self.data:
            return True

        return False

    def has_any_permission(self, action_list):
        """
        Receive a list of tuple's with their action_name and parameters values
        e.g:
        [('can_view:module', {'module_id': 1}), ('can_manage:module', {'module_id': 12})]
        """

        for action_name, parameter_values in action_list:
            if self.has_permission(action_name, **parameter_values):
                return True

        return False


