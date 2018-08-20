from __future__ import unicode_literals, absolute_import, print_function

from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from django_permissions.django_permissions.validations import ValidatingGrantModel


@python_2_unicode_compatible
class Permission(models.Model):

    code = models.CharField(
        max_length=256,
        help_text='The formal slug for this role, which should be unique',
        unique=True,
    )

    description = models.TextField(
        help_text='Description for this role',
        blank=True
    )

    scope = models.CharField(
        max_length=256,
        help_text='The permission scope',
    )

    parameters_definition = ArrayField(
        models.CharField(max_length=32),
        help_text='A set of strings which are the parameters for this role. Entered as a JSON list.',
        default=list,
    )

    def __repr__(self):
        return 'Permission(%r, parameters=%r)' % (self.code, self.parameters)

    def __str__(self):
        return self.code


class UserGrant(ValidatingGrantModel, models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='user_grants',
        on_delete=models.CASCADE,
    )

    permission = models.ForeignKey(
        'Permission',
        related_name='permission_user_grants',
        on_delete=models.CASCADE,
    )

    parameter_values = JSONField(
        blank=True,
        default=dict,
    )

    class Meta:
        unique_together = ('user', 'permission', 'parameter_values')

    def __repr__(self):
        return 'UserGrant(%r, permission=%r)' % (self.user.first_name, self.permission.code)

    def __str__(self):
        return self.permission.code


class GroupGrant(ValidatingGrantModel, models.Model):

    group = models.ForeignKey(
        'auth.Group',
        related_name='group_grants',
        on_delete=models.CASCADE,
    )

    permission = models.ForeignKey(
        'Permission',
        related_name='permission_group_grants',
        on_delete=models.CASCADE,
    )

    parameter_values = JSONField(
        blank=True,
        default=dict,
    )

    class Meta:
        unique_together = ('group', 'permission', 'parameter_values')

    def __repr__(self):
        return 'GroupGrant(%r, permission=%r)' % (self.group.name, self.permission.code)

    def __str__(self):
        return self.permission.code
