from django.test import TestCase
from django.conf import settings
from model_mommy import mommy

from ..services import has_permission


class HasPermissionTestCase(TestCase):

    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.can_view_code = "can_view:module"
        self.can_view_permission = mommy.make("django_permissions.Permission", code=self.can_view_code)

    def test_user_has_permission(self):
        mommy.make("django_permissions.UserGrant", user=self.user, permission=self.can_view_permission)
        response = has_permission(self.user.id, self.can_view_permission)
        self.assertTrue(response)
