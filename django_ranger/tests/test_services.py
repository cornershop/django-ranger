from django.conf import settings
from django.test import TestCase
from model_mommy import mommy

from ..services import PermissionManager


class HasPermissionTestCase(TestCase):

    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.group = mommy.make("auth.Group")
        self.user.groups.add(self.group)
        self.can_view_code = "can_view:module"
        self.can_view_with_param_code = "can_view_with_param:module"
        self.can_view_permission = mommy.make("django_ranger.Permission", code=self.can_view_code)
        self.can_view_permission_with_param = mommy.make("django_ranger.Permission",
                                                         code=self.can_view_with_param_code,
                                                         parameters_definition=["model_id"])

    def test_permission_manager_has_permission(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_ranger.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)
        mommy.make("django_ranger.UserGrant", user=self.user, permission=self.can_view_permission)

        user_permission = PermissionManager(self.user)
        response = user_permission.has_permission(self.can_view_code)
        self.assertTrue(response)

    def test_permission_manager_has_permission_without_param(self):

        mommy.make("django_ranger.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values={})
        mommy.make("django_ranger.UserGrant", user=self.user, permission=self.can_view_permission)

        user_permission = PermissionManager(self.user)
        response = user_permission.has_permission(self.can_view_code, model_id=1)
        self.assertTrue(response)

    def test_permission_manager_has_not_permission(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_ranger.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)

        user_permission = PermissionManager(self.user)
        response = user_permission.has_permission(self.can_view_with_param_code, model_id=2)
        self.assertFalse(response)

    def test_permission_manager_has_not_permission_without_param(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_ranger.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)

        user_permission = PermissionManager(self.user)
        response = user_permission.has_permission(self.can_view_with_param_code)
        self.assertFalse(response)

    def test_permission_manager_has_any_permission(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_ranger.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)

        action_list = [(self.can_view_with_param_code, {'model_id': 1}), (self.can_view_code, {})]

        user_permission = PermissionManager(self.user)
        response = user_permission.has_any_permission(action_list)
        self.assertTrue(response)

    def test_permission_manager_has_not_any_permission(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_ranger.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)

        action_list = [(self.can_view_with_param_code, {'model_id': 2}), (self.can_view_code, {})]

        user_permission = PermissionManager(self.user)
        response = user_permission.has_any_permission(action_list)
        self.assertFalse(response)
