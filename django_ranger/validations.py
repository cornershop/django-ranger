from collections import Counter

from .exceptions import ParameterError


class ValidatingGrantModel(object):
    """
    A validation Mixin for  UserGrant and GroupGrant models.

    it verifies that the `parameter_values` of the grant instance be consistent
    with the parameters defined in the permission instance.

    """
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not hasattr(self, "permission"):
            raise AttributeError(u"The model must have a permission field")

        if not hasattr(self, "parameter_values"):
            raise AttributeError(u"The model must have a parameter_values field")

        definition = self.permission.parameters_definition
        values = self.parameter_values.keys()
        if Counter(definition) != Counter(values) and values != []:
            msg = u"parameter_values content is inconsistent with permission.parameters_definition {}-{}".format(
                definition, values)
            raise ParameterError(msg)
        super(ValidatingGrantModel, self).save(force_insert, force_update, using, update_fields)
