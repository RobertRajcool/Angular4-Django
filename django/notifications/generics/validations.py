from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import json
from django.core.validators import EmailValidator


def validate_nf_non_user_recipients(value):
    """
        Validates recipients data i.e contains name & email , their formats
    """
    value = json.loads(value)
    if not isinstance(value, list):
        raise ValidationError(
            _('Unsupported format, %(value)s is not type list'),
            params={'value': value},
        )
    else:
        for val in value:
            if not len(val) == 2:
                raise ValidationError(
                    _('%(value)s parameters does not match requried arguments, required arguments:2 , provided %(length)s'),
                    params={'value': val, 'length': len(val)}
                )
            elif (not isinstance(val, tuple)) and (not isinstance(val, list)):
                raise ValidationError(
                    _('Unsupported format, %(value)s is not type list'),
                    params={'value': val},
                )
            else:
                if not isinstance(val[0], str):
                    raise ValidationError(
                        _('Unsupported format, %(value)s is not type str'),
                        params={'value': val[0]},
                    )

                EmailValidator(val[1])
