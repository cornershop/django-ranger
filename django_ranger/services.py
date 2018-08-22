# Use modern Python
from __future__ import unicode_literals, absolute_import, print_function

from django.utils.functional import cached_property

from .models import Permission, UserGrant, GroupGrant


class PermissionManager(object):
    """
    This class allows managing user permissions.

    It is instantiated with a user instance and enlists all their permissions
     grants to achieve a better performance in multiple permission verifications.
    """

    def __init__(self, user):
        self.user = user

    @cached_property
    def _grants(self):
        user_grants = list(self.user.user_grants.select_related('permission').all())
        group_grants = list(GroupGrant.objects.filter(group__in=self.user.groups.all()).select_related('permission'))
        return map(_convert_group_grant_to_user_grant, group_grants) + user_grants

    def has_permission(self, action_name, **parameter_values):
        """
        Verifies if the instantiated user has the given permission with
        the given parameters.
        """
        permission = Permission.objects.get(code=action_name)
        expected_grant = UserGrant(permission=permission, parameter_values=parameter_values)
        for grant in self._grants:
            if grant.complies(expected_grant):
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


def _convert_group_grant_to_user_grant(group_grant):
    user_grant = UserGrant()
    user_grant.permission = group_grant.permission
    user_grant.parameter_values = group_grant.parameter_values
    return user_grant
