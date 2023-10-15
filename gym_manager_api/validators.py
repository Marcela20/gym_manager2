from django.core.exceptions import ValidationError
import re
def phone_number_validator(value):
    reg = re.compile('^\d+$')
    if not reg.match(value) :
        raise ValidationError('not a valid phone number!')