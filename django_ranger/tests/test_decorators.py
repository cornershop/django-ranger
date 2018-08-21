from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from rest_framework.response import Response
from model_mommy import mommy

from ..decorators import permission_required
from ..models import UserGrant


class DecoratorTestCase(TestCase):

    def setUp(self):
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.group = mommy.make("auth.Group")
        self.user.groups.add(self.group)
        self.can_view_code = "can_view:module"
        self.can_view_permission = mommy.make("django_ranger.Permission",
                                              code=self.can_view_code,
                                              parameters_definition=['country_code'])

    def test_has_permission(self):
        UserGrant.objects.create(user=self.user,
                                 permission=self.can_view_permission,
                                 parameter_values={'country_code': 'MX'})

        action_list = [('can_view:module', {'country_code': "MX"})]

        @permission_required(action_list)
        def view(*args, **kwargs):
            return Response()

        rf = RequestFactory()
        request = rf.get("/url/")
        request.user = self.user
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_has_not_permission(self):
        UserGrant.objects.create(user=self.user,
                                 permission=self.can_view_permission,
                                 parameter_values={'country_code': 'CL'})

        action_list = [('can_view:module', {'country_code': "MX"})]

        @permission_required(action_list)
        def view(*args, **kwargs):
            return Response()

        rf = RequestFactory()
        request = rf.get("/url/")
        request.user = self.user
        response = view(request)

        self.assertEqual(response.status_code, 302)

