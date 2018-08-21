from functools import wraps

from django.http import HttpResponseRedirect

from .services import PermissionManager


def permission_required(action_list=None, *args, **kwargs):
    """
    This decorator verifies if the user has permissions to perform
    any action contained by `action_list`.

    The `action_list param expect the structure described bellow:

    [('can_view:module', {'module_id': 1}), ('can_manage:module', {'module_id': 12})]

    This decorator only works over django function based views. This is not tested for
    rest framework function based view.
    """
    def renderer(function):
        @wraps(function)
        def wrapper(obj, *args, **kwargs):
            try:
                request = obj
                user = obj.user
            except AttributeError:
                raise ValueError("ERROR: The specified object is not a proper request")

            user_permission = PermissionManager(user)
            if not user_permission.has_any_permission(action_list):
                # TODO change URL for a url set in the django settings
                return HttpResponseRedirect("/accounts/login/?next=" + request.path)

            return function(obj, *args, **kwargs)
        return wrapper
    return renderer
