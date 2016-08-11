from werkzeug.exceptions import UnprocessableEntity


class FlumpUnprocessableEntity(UnprocessableEntity):
    def __init__(self, errors=None, *args, **kwargs):
        super(FlumpUnprocessableEntity, self).__init__(*args, **kwargs)

        self.errors = errors
