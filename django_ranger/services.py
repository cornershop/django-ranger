# Use modern Python
from __future__ import unicode_literals, absolute_import, print_function

from django.utils.functional import cached_property
from django.db.models import Q, QuerySet

from .models import Permission, UserGrant, GroupGrant
from .exceptions import DoesNotExist, PermissionNotRevocable


class PermissionManager(object):
    """
    This class allows managing user permissions.

    It is instantiated with a user instance and enlists all their permissions
     grants to achieve a better performance in multiple permission verifications.
    """
    DoesNotExist = DoesNotExist
    PermissionNotRevocable = PermissionNotRevocable

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

    def grant_permission(self, action_name, **parameter_values):
        """
        Creates an UserGrant for the instanced user with the given permission.
        If the grant already exists, this method does nothing.
        """
        permission = Permission.objects.get(code=action_name)
        query = Q(user=self.user, permission=permission) & (Q(parameter_values=parameter_values) | Q(parameter_values={}))
        if not UserGrant.objects.filter(query).exists():
            UserGrant.objects.create(permission=permission, user=self.user, parameter_values=parameter_values)

    def revoke_permission(self, action_name, **parameter_values):
        """
        Delete a UserGrant for the instanced user with the given permission.

        If the grant doesn't exists, this method raise an DoesNotExist exception.

        But if the user has this permission from a different way (e.g through GroupGrant or permission without params),
        it raise a PermissionNotRevocable exception.
        """
        permission = Permission.objects.get(code=action_name)
        user_grant = UserGrant.objects.filter(user=self.user, permission=permission, parameter_values=parameter_values)
        if user_grant.exists():
            user_grant.delete()
        elif not self.has_permission(action_name, **parameter_values):
            raise self.DoesNotExist("Permission {} does not granted".format(permission.code))
        else:
            raise self.PermissionNotRevocable("Permission {} does not granted".format(permission.code))

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

        self.is_filtered_by_permission = False
        self.permission_manager = permission_manager
        self.permissions_definition = permissions_definition
        super(RangerQuerySet, self).__init__(model, query, *args, **kwargs)

    def all(self):
        """
        Returns a new QuerySet that is a copy of the current one. This allows a
        QuerySet to proxy for a model manager in some cases.
        """
        clone = self._clone()
        if not self.is_filtered_by_permission:
            clone = self._filtered_by_permissions(clone)
            self.is_filtered_by_permission = True
        return clone

    def filter(self, *args, **kwargs):
        clone = super(RangerQuerySet, self).filter(*args, **kwargs)
        if not self.is_filtered_by_permission:
            clone = self._filtered_by_permissions(clone)
            self.is_filtered_by_permission = True
        return clone

    def _filtered_by_permissions(self, clone):
        """
        Returns a new QuerySet instance filtered by the user permissions.
        """

        # obtains the needed grant for this query.
        grants = filter(lambda x: x.complies_any(self.permissions_definition), self.permission_manager.get_grants())
        if not grants:
            return self.none()

        query = self._create_query(grants)
        clone.query.add_q(query)
        return clone

    def _create_query(self, grants):
        """
        Returns a Query expression built off the user grants.
        """
        query_list = []

        for grant in filter(lambda x: x.complies_any(self.permissions_definition), grants):
            params = self._convert_to_dict_query(grant)

            if params == {}:
                # if exists a permission without params, the other permissions are ignored
                return Q(**params)

            query_list.append(Q(**params))

        query = query_list.pop()
        for item_query in query_list:
            query = query | item_query

        return query

    def _convert_to_dict_query(self, grant):
        """
        Returns a dict that can be passed by params to the .filter() method
        for make querying.
        """
        action = filter(lambda x: grant.complies_any([x]), self.permissions_definition)[0]
        lookups = action[1]
        params = {}
        for key in grant.parameter_values.keys():
            lookup_key = lookups.get(key, key)
            params[lookup_key] = grant.parameter_values[key]

        return params

