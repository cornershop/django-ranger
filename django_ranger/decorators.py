from functools import wraps

from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.response import Response

from .services import PermissionManager


def permission_required(action_list=None, permission_class=None, *args, **kwargs):
    """
    This decorator verifies if the user has permissions to perform
    any action contained by `action_list`.

    The `action_list` param expect the structure described bellow:

    [('can_view:module', {'module_id': 1}), ('can_manage:module', {'module_id': 12})]

    This decorator only works over django function based views. This is not tested for
    rest framework function based view.
    """
    final_action_list = action_list or []
    for action in final_action_list:
        if type(action) != tuple:
            action = (action, {})
        final_action_list.append(action)

    action_list = final_action_list

    def renderer(function):
        @wraps(function)
        def wrapper(obj, *args, **kwargs):
            if not hasattr(obj, "user"):
                raise ValueError("ERROR: The specified object is not a proper request")

            request = obj
            user = obj.user

            if not user.is_authenticated():
                return HttpResponseRedirect("/accounts/login/?next=" + request.path)

            if permission_class:
                permissions_list = permission_class(request=obj, **kwargs).get_permissions()
            else:
                permissions_list = action_list

            user_permission = PermissionManager(user)
            if not user_permission.has_any_permission(permissions_list):
                # TODO change URL for a url set in the django settings
                return HttpResponseRedirect("/accounts/login/?next=" + request.path)

            return function(obj, *args, **kwargs)
        return wrapper
    return renderer


def api_permission_required(action_list=None, permission_class=None, *args, **kwargs):
    """
    This decorator verifies if the user has permissions to perform
    any action contained by `action_list`.

    The `action_list` param expect the structure described bellow:

    [('can_view:module', {'module_id': 1}), ('can_manage:module', {'module_id': 12})]

    This decorator only works over api views.
    """
    def renderer(function):
        @wraps(function)
        def wrapper(obj, *args, **kwargs):
            if not hasattr(obj, "user"):
                raise ValueError("ERROR: The specified object is not a proper request")

            user = obj.user

            if not user.is_authenticated():
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            if permission_class:
                permissions_list = permission_class(request=obj, **kwargs).get_permissions()
            else:
                permissions_list = action_list

            user_permission = PermissionManager(user)
            if not user_permission.has_any_permission(permissions_list):
                return Response(status=status.HTTP_403_FORBIDDEN)

            return function(obj, *args, **kwargs)
        return wrapper
    return renderer
