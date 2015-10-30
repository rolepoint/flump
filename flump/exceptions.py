from werkzeug.exceptions import UnprocessableEntity


class FlumpUnprocessableEntity(UnprocessableEntity):
    def __init__(self, *args, errors=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.errors = errors
