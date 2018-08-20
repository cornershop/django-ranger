from django.conf import settings
from django.test import TestCase
from model_mommy import mommy

from ..exceptions import ParameterError
from ..models import UserGrant


class ModelsTestCase(TestCase):

    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.group = mommy.make("auth.Group")
        self.user.groups.add(self.group)
        self.can_view_code = "can_view:module"

    def test_create_consistent_user_grant(self):
        can_view_permission = mommy.make("django_ranger.Permission", code=self.can_view_code)
        created = UserGrant.objects.create(user=self.user, permission=can_view_permission)
        self.assertTrue(created)

    def test_create_inconsistent_user_grant(self):
        can_view_permission = mommy.make("django_ranger.Permission",
                                         code=self.can_view_code)

        with self.assertRaises(ParameterError):
            UserGrant.objects.create(user=self.user,
                                     permission=can_view_permission,
                                     parameter_values={"model_id": 1})

    def test_create_grant_without_param(self):
        can_view_permission = mommy.make("django_ranger.Permission",
                                         code=self.can_view_code,
                                         parameters_definition=['model_id'])

        created = UserGrant.objects.create(user=self.user, permission=can_view_permission)
        self.assertTrue(created)

    def test_permission_repr(self):
        can_view_permission = mommy.make("django_ranger.Permission", code=self.can_view_code)
        expected_repr = 'Permission(%r, parameters=[])' % self.can_view_code
        self.assertEqual(can_view_permission.__repr__(), expected_repr)

    def test_permission_str(self):
        can_view_permission = mommy.make("django_ranger.Permission", code=self.can_view_code)
        self.assertEqual(can_view_permission.__str__(), self.can_view_code)

    def test_user_grant_repr(self):
        can_view_permission = mommy.make("django_ranger.Permission", code=self.can_view_code)
        user_grant = mommy.make("django_ranger.UserGrant", user=self.user, permission=can_view_permission)
        expected_repr = 'UserGrant(%r, permission=%r)' % (self.user.first_name, self.can_view_code)
        self.assertEqual(user_grant.__repr__(), expected_repr)

    def test_user_grant_str(self):
        can_view_permission = mommy.make("django_ranger.Permission", code=self.can_view_code)
        user_grant = mommy.make("django_ranger.UserGrant", user=self.user, permission=can_view_permission)
        self.assertEqual(user_grant.__str__(), self.can_view_code)

    def test_group_grant_repr(self):
        can_view_permission = mommy.make("django_ranger.Permission", code=self.can_view_code)
        group_grant = mommy.make("django_ranger.GroupGrant", group=self.group, permission=can_view_permission)
        expected_repr = 'GroupGrant(%r, permission=%r)' % (self.group.name, self.can_view_code)
        self.assertEqual(group_grant.__repr__(), expected_repr)

    def test_group_grant_str(self):
        can_view_permission = mommy.make("django_ranger.Permission", code=self.can_view_code)
        group_grant = mommy.make("django_ranger.GroupGrant", group=self.group, permission=can_view_permission)
        self.assertEqual(group_grant.__str__(), self.can_view_code)

