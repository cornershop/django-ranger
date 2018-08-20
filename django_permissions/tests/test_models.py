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
        can_view_permission = mommy.make("django_permissions.Permission", code=self.can_view_code)
        created = UserGrant.objects.create(user=self.user, permission=can_view_permission)
        self.assertTrue(created)

    def test_create_inconsistent_user_grant(self):
        can_view_permission = mommy.make("django_permissions.Permission",
                                         code=self.can_view_code)

        with self.assertRaises(ParameterError):
            UserGrant.objects.create(user=self.user,
                                     permission=can_view_permission,
                                     parameter_values={"model_id": 1})
