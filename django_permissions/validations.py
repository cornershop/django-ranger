from django_permissions.django_permissions.exceptions import ParameterError


class ValidatingGrantModel(object):
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        definition = self.permission.parameters_definition
        values = self.parameter_values.keys()
        if definition != values and values != []:
            msg = u"parameter_values content is inconsistent with permission.parameters_definition {}-{}".format(
                definition, values)
            raise ParameterError(msg)
        super(ValidatingGrantModel, self).save(force_insert, force_update, using, update_fields)