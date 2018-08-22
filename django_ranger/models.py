from __future__ import unicode_literals, absolute_import, print_function

from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .validations import ValidatingGrantModel


@python_2_unicode_compatible
class Permission(models.Model):
    """
    A model class that stores permissions. It represents
    the actions that the users can do.
    """

    code = models.CharField(
        max_length=256,
        help_text='The formal code for this role, which should be unique',
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
        help_text='A list of strings which are the parameters for this role.',
        default=list,
    )

    def __repr__(self):
        return 'Permission(%r, parameters=%r)' % (self.code, self.parameters_definition)

    def __str__(self):
        return self.code


class UserGrant(ValidatingGrantModel, models.Model):
    """
    A user grant model. This grant works as roles level permission over all
    their instance when `parameters_values` is empty and work as object level
    permission when it has any value. The parameter_values must correspond
    with the `parameters_definition` of the permission.

    """

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

    def complies(self, expected_grant):
        """
        Verifies if the grant match with the expected grant.
        """
        permissions_are_equal = self.permission == expected_grant.permission
        parameters_are_equal = self.parameter_values == expected_grant.parameter_values
        return permissions_are_equal and (parameters_are_equal or self.parameter_values == {})


class GroupGrant(ValidatingGrantModel, models.Model):
    """
    A group grant model. Works like UserGrant, but grants permissions to user
    groups. It allows create permissions groups and set or remove permissions
    of the users more easily.
    """

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
