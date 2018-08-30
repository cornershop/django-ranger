# Use modern Python
from __future__ import unicode_literals, absolute_import, print_function

from django.utils.functional import cached_property
from django.db.models import Q, QuerySet

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
        return map(lambda x: x.to_user_grant(self.user), group_grants) + user_grants

    def get_grants(self):
        return self._grants

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


class RangerQuerySet(QuerySet):
    """
    This is a reimplementation of QuerySet to make querying filtering by user grants.

    It needs to be instantiated with a Model class or a QuerySet instance,
    a user permission manager (PermissionManager) instance, and their
    permission definitions.

    Returns a RangerQuerySet filtered by the requested permissions

    """

    def __init__(self, model, permission_manager=None, permissions_definition=list, query=None, *args, **kwargs):
        if isinstance(model, QuerySet):
            queryset = model
            model = model.model
            query = queryset.query.clone()

        self.permission_manager = permission_manager
        self.permissions_definition = permissions_definition
        super(RangerQuerySet, self).__init__(model, query, *args, **kwargs)

    def all(self, _filter_by_permissions=True):
        """
        Returns a new QuerySet that is a copy of the current one. This allows a
        QuerySet to proxy for a model manager in some cases.
        """
        return self.filter(_filter_by_permissions)

    def filter(self, _filter_by_permissions=True, *args, **kwargs):
        """
        Returns a new QuerySet instance with the args ANDed to the existing
        set filtered by the user permissions.
        """
        queryset = self._filter_or_exclude(False, *args, **kwargs)
        if _filter_by_permissions and self.permission_manager and self.permissions_definition:
            queryset = self._filtered_by_permissions(queryset)

        return queryset

    def _filtered_by_permissions(self, queryset):
        """
        Returns a new QuerySet instance filtered by the user permissions.
        """

        # obtains the needed grant for this query.
        grants = filter(lambda x: x.complies_any(self.permissions_definition), self.permission_manager.get_grants())
        if not grants:
            return self.none()

        query = self._create_query(grants)
        queryset = queryset.filter(False, query)

        return queryset

    def _create_query(self, grants):
        """
        Returns a Query expression built off the user grants.
        """
        query_list = []

        for action in self.permissions_definition:
            grants = filter(lambda x: x.complies_any([action]), grants)
            if not grants:
                continue

            for grant in grants:
                params = self._convert_to_dict_query(grant, action[1])
                query_list.append(Q(**params))

        query = query_list.pop()
        for item_query in query_list:
            query = query | item_query

        return query

    @staticmethod
    def _convert_to_dict_query(grant, lookups):
        """
        Returns a dict that can be passed by params to the .filter() method
        for make querying.
        """
        params = {}
        for key in grant.parameter_values.keys():
            lookup_key = lookups.get(key, key)
            params[lookup_key] = grant.parameter_values[key]

        return params

