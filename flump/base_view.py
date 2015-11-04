from flask import request
from flask.views import MethodView
from werkzeug.exceptions import PreconditionFailed, PreconditionRequired
from werkzeug.exceptions import NotImplemented as WerkzeugNotImplemented


from .schemas import make_data_schema, make_response_schema


class BaseFlumpView:
    """
    A base view from which all views provided to `FlumpBlueprint` must
    inherit.

    View classes which inherit from this must provide `get_entity` and
    `delete_entity` methods.
    """

    def __init__(self, resource_schema, resource_name, endpoint):
        self.resource_schema = resource_schema
        self.resource_name = resource_name
        self.endpoint = endpoint

    def get_entity(self, entity_id, **kwargs):
        """
        Should provide a method of retrieving a single entity given the
        `entity_id`.
        """
        raise NotImplemented

    def delete_entity(self, entity):
        """
        Should provide a method of deleting a single entity given the `entity`.
        """
        raise NotImplemented

    @property
    def data_schema(self):
        """
        Returns a Schema describing the main jsonapi format for the
        current `resource_schema`.
        """
        return make_data_schema(self.resource_schema,
                                self._get_sparse_fieldset())

    @property
    def response_schema(self):
        """
        A schema describing the format of a response according to jsonapi.
        """
        return make_response_schema(self.resource_schema,
                                    only=self._get_sparse_fieldset())

    def get_many(self):
        raise WerkzeugNotImplemented("Coming Soon.")

    def get_single(self, entity_id=None, **kwargs):
        raise WerkzeugNotImplemented

    def get(self, entity_id=None, **kwargs):
        return (
            self.get_single(entity_id, **kwargs) if entity_id
            else self.get_many()
        )

    def post(self, **kwargs):
        raise WerkzeugNotImplemented

    def delete(self, entity_id, **kwargs):
        raise WerkzeugNotImplemented

    def patch(self, entity_id, **kwargs):
        raise WerkzeugNotImplemented("Coming Soon.")

    def _get_sparse_fieldset(self):
        """
        Returns a list of fields which have been requested to be returned.
        """
        requested_fields = request.args.get(
            'fields[{}]'.format(self.resource_name)
        )
        if requested_fields:
            requested_fields = set(requested_fields.split(','))
            return requested_fields

    def _verify_etag(self, entity):
        """
        Verifies that the given etag is valid, if not raises a
        PreconditionFailed.
        """
        if not request.headers.get('If-Match'):
            raise PreconditionRequired

        if not self._etag_matches(entity):
            raise PreconditionFailed(
                'Incorrect or missing etag in the In-Match header'
            )

    def _etag_matches(self, entity):
        """
        Returns a boolean indicating whether the etag is valid.
        """
        return any(i in request.if_match for i in (str(entity.etag), '*'))


class _FlumpMethodView(MethodView):
    def __init__(self, flump_view):
        self.flump_view = flump_view

    def get(self, *args, **kwargs):
        return self.flump_view.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.flump_view.post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.flump_view.delete(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.flump_view.patch(*args, **kwargs)
