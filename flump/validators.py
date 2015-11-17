from flask import request

from marshmallow.exceptions import ValidationError
from marshmallow.validate import Validator


class Immutable(Validator):
    """
    Validator which ensures that a field cannot be updated through a `PATCH`
    request.
    """

    def __call__(self, value):
        if request.method == 'PATCH':
            raise ValidationError("Can't update immutable fields.")

        return value
