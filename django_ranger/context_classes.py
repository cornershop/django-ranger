class BasePermissionContext(object):

    def __init__(self, request=None, user=None, **kwargs):
        self.request = request
        self.user = user
        self.kwargs = kwargs

    def get_user(self):
        if self.user:
            return self.user
        if self.request and self.request.user and self.request.is_authenticated():
            return self.request.user
        return None

    def get_permissions(self):
        return self.context_data()

    def context_data(self):
        raise NotImplementedError()
