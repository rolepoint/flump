from werkzeug.exceptions import NotImplemented as WerkzeugNotImplemented


class Put:
    def put(self, entity_id, **kwargs):
        raise WerkzeugNotImplemented
