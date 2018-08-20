from django.conf import settings
from django.test import TestCase
from model_mommy import mommy

from ..models import Permission
from ..services import has_permission, has_group_grant, has_user_grant, PermissionManager


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

    def test_has_permission(self):
        mommy.make("django_permissions.UserGrant", user=self.user, permission=self.can_view_permission)
        response = has_permission(self.user.id, self.can_view_permission)
        self.assertTrue(response)

    def test_has_not_permission(self):
        response = has_permission(self.user.id, self.can_view_permission)
        self.assertFalse(response)

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

    def test_permission_manager_has_permission(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_permissions.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)
        mommy.make("django_permissions.UserGrant", user=self.user, permission=self.can_view_permission)

        user_permission = PermissionManager(self.user)
        self.assertEqual(user_permission.group_grants.count(), 1)
        self.assertEqual(user_permission.user_grants.count(), 1)
        response = user_permission.has_permission(self.can_view_code)
        self.assertTrue(response, user_permission.data)

    def test_permission_manager_has_not_permission(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_permissions.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)

        user_permission = PermissionManager(self.user)
        self.assertEqual(user_permission.group_grants.count(), 1)
        self.assertEqual(user_permission.user_grants.count(), 0)
        response = user_permission.has_permission(self.can_view_code)
        self.assertFalse(response, user_permission.data)



