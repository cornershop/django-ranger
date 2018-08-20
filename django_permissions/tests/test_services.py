from django.conf import settings
from django.test import TestCase
from model_mommy import mommy

from ..models import Permission
from ..services import has_permission, has_group_grant, has_user_grant


class HasPermissionTestCase(TestCase):

    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.group = mommy.make("auth.Group")
        self.user.groups.add(self.group)
        self.can_view_code = "can_view:module"
        self.can_view_with_param_code = "can_view_with_param:module"
        self.can_view_permission = mommy.make("django_permissions.Permission", code=self.can_view_code)
        self.can_view_permission_with_param = mommy.make("django_permissions.Permission",
                                                         code=self.can_view_with_param_code,
                                                         parameters_definition=["model_id"])

    def test_user_has_permission(self):
        mommy.make("django_permissions.UserGrant", user=self.user, permission=self.can_view_permission)
        response = has_permission(self.user.id, self.can_view_permission)
        self.assertTrue(response)

    def test_permission_does_not_exist(self):
        with self.assertRaises(Permission.DoesNotExist):
            has_permission(self.user.id, "has_unexpected_permission:module")

    def test_user_has_permission_with_params(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_permissions.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)
        response = has_user_grant(self.user.id, self.can_view_permission_with_param, params)
        self.assertTrue(response)

    def test_user_has_not_permission_with_params(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_permissions.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)
        response = has_user_grant(self.user.id, self.can_view_permission_with_param)
        self.assertFalse(response)

    def test_user_has_not_permission(self):
        response = has_user_grant(self.user.id, self.can_view_permission)
        self.assertFalse(response)

    def test_user_group_has_permission(self):
        mommy.make("django_permissions.GroupGrant", group=self.group, permission=self.can_view_permission)
        response = has_group_grant(self.user.id, self.can_view_permission)
        self.assertTrue(response)

    def test_user_group_has_permission_with_params(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_permissions.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)
        response = has_group_grant(self.user.id, self.can_view_permission_with_param, params)
        self.assertTrue(response)

    def test_user_group_has_not_permission_with_params(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_permissions.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)
        response = has_group_grant(self.user.id, self.can_view_permission_with_param)
        self.assertFalse(response)

    def test_user_group_has_not_permission(self):
        response = has_group_grant(self.user.id, self.can_view_permission)
        self.assertFalse(response)



