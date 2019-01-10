from django.conf import settings
from django.test import TestCase
from model_mommy import mommy

from ..models import UserGrant
from ..services import PermissionManager, RangerQuerySet


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

    def test_permission_manager_grant_permission(self):
        params = {
            "model_id": 1
        }

        user_permission = PermissionManager(self.user)
        user_permission.grant_permission(self.can_view_with_param_code, **params)
        user_grant = UserGrant.objects.filter(permission__code=self.can_view_with_param_code, user=self.user, parameter_values=params)
        self.assertTrue(user_grant.exists())

    def test_permission_manager_not_grant_permission_when_have_one_without_params(self):
        params = {
            "model_id": 1
        }
        mommy.make("django_ranger.UserGrant", user=self.user, permission=self.can_view_permission_with_param)

        user_permission = PermissionManager(self.user)
        user_permission.grant_permission(self.can_view_with_param_code, **params)
        user_grant = UserGrant.objects.filter(permission__code=self.can_view_with_param_code, user=self.user, parameter_values=params)
        self.assertFalse(user_grant.exists())

    def test_permission_manager_revoke_permission(self):
        params = {
            "model_id": 1
        }
        mommy.make(
            "django_ranger.UserGrant",
            user=self.user,
            permission=self.can_view_permission_with_param,
            parameter_values=params
        )

        user_permission = PermissionManager(self.user)
        user_permission.revoke_permission(self.can_view_with_param_code, **params)
        user_grant = UserGrant.objects.filter(permission__code=self.can_view_permission_with_param, user=self.user, parameter_values=params)
        self.assertFalse(user_grant.exists())

    def test_permission_manager_revoke_permission_does_not_exists(self):
        params = {
            "model_id": 1
        }
        user_permission = PermissionManager(self.user)
        with self.assertRaises(PermissionManager.DoesNotExist):
            user_permission.revoke_permission(self.can_view_with_param_code, **params)

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


class RangerQuerySetTestCase(TestCase):

    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL, is_active=True)
        self.user = mommy.make(settings.AUTH_USER_MODEL, is_active=False)
        self.group = mommy.make("auth.Group")
        self.user.groups.add(self.group)
        self.can_view_code = "can_view_users"
        self.can_view_with_param_code = "can_view_with_param_users"
        self.can_view_permission = mommy.make("django_ranger.Permission", code=self.can_view_code)
        self.can_view_permission_with_param = mommy.make("django_ranger.Permission",
                                                         code=self.can_view_with_param_code,
                                                         parameters_definition=["active"])

    def test_get_all_by_permissions(self):
        params = {
            "active": True
        }
        mommy.make("django_ranger.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)

        action_list = [(self.can_view_with_param_code, {'active': 'is_active'}), (self.can_view_code, {})]
        user_permission = PermissionManager(self.user)
        user_model = self.user._meta.model

        queryset = RangerQuerySet(user_model, user_permission, action_list)
        queryset = queryset.all()
        self.assertEqual(queryset.count(), 1)

    def test_get_all_by_permissions_without_params(self):

        mommy.make("django_ranger.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values={})

        action_list = [(self.can_view_with_param_code, {'active': 'is_active'}), (self.can_view_code, {})]
        user_permission = PermissionManager(self.user)
        user_model = self.user._meta.model

        queryset = RangerQuerySet(user_model, user_permission, action_list)
        queryset = queryset.all()
        self.assertEqual(queryset.count(), 2)

    def test_filter_by_permissions(self):
        params = {
            "active": True
        }
        mommy.make("django_ranger.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)

        action_list = [(self.can_view_with_param_code, {'active': 'is_active'}), (self.can_view_code, {})]
        user_permission = PermissionManager(self.user)
        user_model = self.user._meta.model

        queryset = RangerQuerySet(user_model, user_permission, action_list)
        queryset = queryset.filter()
        self.assertEqual(queryset.count(), 1)

    def test_filter_queryset_by_permissions(self):
        params = {
            "active": True
        }
        mommy.make("django_ranger.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values=params)

        action_list = [(self.can_view_with_param_code, {'active': 'is_active'}), (self.can_view_code, {})]
        user_permission = PermissionManager(self.user)
        user_queryset = self.user._meta.model.objects.filter()

        queryset = RangerQuerySet(user_queryset, user_permission, action_list)
        queryset = queryset.filter()
        self.assertEqual(queryset.count(), 1)

    def test_filter_queryset_by_permissions_without_params(self):

        mommy.make("django_ranger.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values={})

        action_list = [(self.can_view_with_param_code, {'active': 'is_active'}), (self.can_view_code, {})]
        user_permission = PermissionManager(self.user)
        user_queryset = self.user._meta.model.objects.filter(is_active=False)

        queryset = RangerQuerySet(user_queryset, user_permission, action_list)
        queryset = queryset.filter()
        self.assertEqual(queryset.count(), 1)

    def test_filter_queryset_by_permissions_using_filter(self):

        mommy.make("django_ranger.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values={'active': True})
        mommy.make("django_ranger.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values={'active': False})

        action_list = [(self.can_view_with_param_code, {'active': 'is_active'}), (self.can_view_code, {})]
        user_permission = PermissionManager(self.user)
        user_queryset = self.user._meta.model.objects.all()

        queryset = RangerQuerySet(user_queryset, user_permission, action_list)
        queryset = queryset.filter(is_active=True)
        self.assertEqual(queryset.count(), 1)

    def test_filter_queryset_with_user_and_group_grants(self):

        mommy.make("django_ranger.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values={'active': True})

        mommy.make("django_ranger.GroupGrant", group=self.group,
                   permission=self.can_view_permission_with_param,
                   parameter_values={})

        action_list = [(self.can_view_with_param_code, {'active': 'is_active'})]
        user_permission = PermissionManager(self.user)
        user_queryset = self.user._meta.model.objects.all()

        queryset = RangerQuerySet(user_queryset, user_permission, action_list)
        queryset = queryset.all()
        self.assertEqual(queryset.count(), 2)

    def test_filter_by_permissions_without_params(self):
        mommy.make("django_ranger.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values={})

        action_list = [(self.can_view_with_param_code, {'active': 'is_active'}), (self.can_view_code, {})]
        user_permission = PermissionManager(self.user)
        user_model = self.user._meta.model

        queryset = RangerQuerySet(user_model, user_permission, action_list)
        queryset = queryset.filter(is_active=False)
        self.assertEqual(queryset.count(), 1)

        queryset = RangerQuerySet(user_model, user_permission, action_list)
        queryset = queryset.filter(is_active=True)
        self.assertEqual(queryset.count(), 1)

    def test_filter_by_permissions_without_params_and_void_filter(self):
        mommy.make("django_ranger.UserGrant", user=self.user,
                   permission=self.can_view_permission_with_param,
                   parameter_values={})

        action_list = [(self.can_view_with_param_code, {'active': 'is_active'}), (self.can_view_code, {})]
        user_permission = PermissionManager(self.user)
        user_model = self.user._meta.model

        queryset = RangerQuerySet(user_model, user_permission, action_list)
        queryset = queryset.filter()
        self.assertEqual(queryset.count(), 2)

    def test_filter_without_permissions(self):

        action_list = [(self.can_view_with_param_code, {'active': 'is_active'}), (self.can_view_code, {})]
        user_permission = PermissionManager(self.user)
        user_model = self.user._meta.model

        queryset = RangerQuerySet(user_model, user_permission, action_list)
        queryset = queryset.filter()
        self.assertEqual(queryset.count(), 0)
