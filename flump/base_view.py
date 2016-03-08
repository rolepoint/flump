from flask import request
from flask.views import MethodView
from werkzeug.exceptions import PreconditionFailed, PreconditionRequired
from werkzeug.exceptions import NotImplemented as WerkzeugNotImplemented


from .schemas import make_data_schema, make_response_schema


class BaseFlumpView:
    """
    A base view from which all views provided to `FlumpBlueprint` must
    inherit.

    Classes which inherit from this must provide `get_entity` and
    `delete_entity` methods. They should also provide provide `RESOURCE_NAME` &
    `SCHEMA` attributes that specify the name of the resource, and the schema
    to use for serialization/desieralization
    """

    def get(self, entity_id=None, **kwargs):
        """
        Handles HTTP GET requests.

        Dispatches to either
        :func:`flump.view.FlumpView.get` or
        :func:`flump.view.FlumpView.get_many` depending on whether an
        `entity_id` has been provided.

        :raises werkzeug.exceptions.NotImplemented: If the method requested has
                                                    not been mixed in.
        """
        if entity_id:
            return self.get_single(entity_id, **kwargs)
        return self.get_many(**kwargs)

    def get_many(self, **kwargs):
        raise WerkzeugNotImplemented

    def get_single(self, entity_id, **kwargs):
        raise WerkzeugNotImplemented

    def post(self, **kwargs):
        raise WerkzeugNotImplemented

    def delete(self, entity_id, **kwargs):
        raise WerkzeugNotImplemented

    def patch(self, entity_id, **kwargs):
        raise WerkzeugNotImplemented

    @property
    def data_schema(self):
        """
        A Schema describing the main jsonapi format for `SCHEMA`.
        """
        return make_data_schema(self.SCHEMA, self._get_sparse_fieldset())

    @property
    def response_schema(self):
        """
        A schema describing the format of a response according to jsonapi.
        """
        return make_response_schema(
            self.SCHEMA,
            only=self._get_sparse_fieldset()
        )

    def get_total_entities(self, **kwargs):
        """
        :returns: Should return an integer of the total number of entities.
        """
        raise NotImplementedError

    def get_many_entities(self, **kwargs):
        """
        :returns: Should return an iterable of entities.

        .. note::

              If the PageSizePagination class has been mixed in, you can
              get the pagination arguments through `self.get_pagination_args()`
        """
        raise NotImplementedError

    def get_entity(self, entity_id, **kwargs):
        """
        Should provide a method of retrieving a single entity given the
        `entity_id` and `**kwargs`.

        :param entity_id: The id of the entity to be retrieved.
        :param \**kwargs: Any other kwargs taken from the url which are used
                          for identifying the entity to be retrieved.
        :returns: The entity identified by `entity_id` and `**kwargs`.
        """
        raise NotImplementedError

    def _get_sparse_fieldset(self):
        """
        Returns a list of fields which have been requested to be returned.
        """
        requested_fields = request.args.get(
            'fields[{}]'.format(self.RESOURCE_NAME)
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
            raise PreconditionFailed

    def _etag_matches(self, entity):
        """
        Returns a boolean indicating whether the etag is valid.
        """
        return any(i in request.if_match for i in (str(entity.etag), '*'))


class _FlumpMethodView(MethodView):
    """
    :func:`flask.Blueprint.add_url_rule` does not allow us to pass instantiated
    instances of :class:`MethodView` as the view_func, so instead we store the
    instantiated instance of our route handlers on this class, and pass args
    and kwargs through to the view methods manually.
    """
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
