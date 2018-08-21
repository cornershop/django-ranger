from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.test.client import RequestFactory
from model_mommy import mommy
from rest_framework.response import Response

from ..decorators import permission_required, api_permission_required
from ..models import UserGrant

action_list = [('can_view:module', {'country_code': "MX"})]


@permission_required(action_list)
def view(*args, **kwargs):
    return Response()


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

        rf = RequestFactory()
        request = rf.get("/url/")
        request.user = self.user
        response = view(request)

        self.assertEqual(response.status_code, 200)

    def test_has_not_permission(self):
        UserGrant.objects.create(user=self.user,
                                 permission=self.can_view_permission,
                                 parameter_values={'country_code': 'CL'})

        rf = RequestFactory()
        request = rf.get("/url/")
        request.user = self.user
        response = view(request)

        self.assertEqual(response.status_code, 302)

    def test_incorrect_request(self):
        UserGrant.objects.create(user=self.user,
                                 permission=self.can_view_permission,
                                 parameter_values={'country_code': 'CL'})

        class Obj(object):
            pass

        with self.assertRaises(ValueError):
            view(Obj)

    def test_user_not_authenticated(self):
        UserGrant.objects.create(user=self.user,
                                 permission=self.can_view_permission,
                                 parameter_values={'country_code': 'CL'})

        rf = RequestFactory()
        request = rf.get("/url/")
        request.user = AnonymousUser()
        response = view(request)

        self.assertEqual(response.status_code, 302)

