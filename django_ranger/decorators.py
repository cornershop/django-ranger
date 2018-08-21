from functools import wraps

from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.response import Response

from .services import PermissionManager


def permission_required(action_list=None, *args, **kwargs):
    """
    This decorator verifies if the user has permissions to perform
    any action contained by `action_list`.

    The `action_list` param expect the structure described bellow:

    [('can_view:module', {'module_id': 1}), ('can_manage:module', {'module_id': 12})]

    This decorator only works over django function based views. This is not tested for
    rest framework function based view.
    """
    def renderer(function):
        @wraps(function)
        def wrapper(obj, *args, **kwargs):
            if not hasattr(obj, "user"):
                raise ValueError("ERROR: The specified object is not a proper request")

            request = obj
            user = obj.user

            if not user.is_authenticated():
                return HttpResponseRedirect("/accounts/login/?next=" + request.path)

            user_permission = PermissionManager(user)
            if not user_permission.has_any_permission(action_list):
                # TODO change URL for a url set in the django settings
                return HttpResponseRedirect("/accounts/login/?next=" + request.path)

            return function(obj, *args, **kwargs)
        return wrapper
    return renderer


def api_permission_required(action_list=None, *args, **kwargs):
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

            user_permission = PermissionManager(user)
            if not user_permission.has_any_permission(action_list):
                return Response(status=status.HTTP_403_FORBIDDEN)

            return function(obj, *args, **kwargs)
        return wrapper
    return renderer
