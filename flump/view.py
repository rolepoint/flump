from flask import request, make_response
from flask.views import MethodView
from werkzeug.exceptions import PreconditionFailed, PreconditionRequired

from .methods import Delete, GetMany, GetSingle, HttpMethods, Patch, Post
from .orm import OrmIntegration
from .pagination import BasePagination
from .fetcher import Fetcher
from .schemas import (EntityData, EntityMetaData, make_data_schema,
                      make_response_schema)
from .web_utils import MIMETYPE


class FlumpView(Patch, Delete, GetMany, GetSingle, Post):
    """
    A base view from which all views provided to `FlumpBlueprint` must
    inherit.

    Classes which inherit from this must override:

    .. data:: ORM_INTEGRATION

        A class which inherits from :class:`.orm.OrmIntegration`

    .. data:: FETCHER

        A class which inherits from :class:`.fetcher.Fetcher`.

    They also may override:

    .. data:: HTTP_METHODS

        A set containing the HTTP Methods to use. See
        :class:`.methods.HttpMethods`

    .. data:: PAGINATOR

        A paginator to use, the default provides NO pagination. If overridden
        must inherit from :class:`.paginator.BasePagination`

    They MUST also provide provide `RESOURCE_NAME` & `SCHEMA` attributes that
    specify the name of the resource, and the schema to use for
    serialization/desieralization.

    They MAY also provide a `VIEW_NAME` attribute that will be used as the name
    of the flask view. This can be used in `url_for` calls. If not provided,
    this will default to `RESOURCE_NAME`.
    """
    HTTP_METHODS = HttpMethods.ALL
    ORM_INTEGRATION = OrmIntegration
    FETCHER = Fetcher
    PAGINATOR = BasePagination
    URL_MAPPING = {
        HttpMethods.GET: '{}/<entity_id>',
        HttpMethods.GET_MANY: '{}',
        HttpMethods.PATCH: '{}/<entity_id>',
        HttpMethods.POST: '{}',
        HttpMethods.DELETE: '{}/<entity_id>'
    }

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
            return self.get_single(entity_id=entity_id, **kwargs)
        return self.get_many(**kwargs)

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
        return make_response_schema(self.SCHEMA,
                                    only=self._get_sparse_fieldset())

    @property
    def fetcher(self):
        """
        Instance cached instantiated version of :data:`.FlumpView.FETCHER`.
        """
        if not getattr(self, '_fetcher', None):
            self._fetcher = self.FETCHER()
        return self._fetcher

    @property
    def paginator(self):
        """
        Instance cached instantiated version of :data:`.FlumpView.PAGINATOR`.
        """
        if not getattr(self, '_paginator', None):
            self._paginator = self.PAGINATOR(self.fetcher)
        return self._paginator

    @property
    def orm_integration(self):
        """
        Instance cached instantiated version of :data:`.FlumpView.ORM_INTEGRATION`.
        """
        if not getattr(self, '_orm_integration', None):
            self._orm_integration = self.ORM_INTEGRATION()
        return self._orm_integration

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

    def _get_etag(self, entity):
        """
        :returns: String of the etag for the given entity.
        """
        return str(entity.etag)

    def _etag_matches(self, entity):
        """
        :returns: Boolean indicating whether the etag is valid.
        """
        return any(i in request.if_match for i in (self._get_etag(entity), '*'))  # noqa

    def _build_entity_data(self, entity):
        '''
        Builds an EntityData struct for an entity.
        '''
        return EntityData(entity.id, self.RESOURCE_NAME,
                          entity, EntityMetaData(self._get_etag(entity)))


def _add_content_type(response):
    response = make_response(response)
    response.headers['Content-Type'] = MIMETYPE

    return response


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
        return _add_content_type(self.flump_view.get(*args, **kwargs))

    def post(self, *args, **kwargs):
        return _add_content_type(self.flump_view.post(*args, **kwargs))

    def delete(self, *args, **kwargs):
        return self.flump_view.delete(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return _add_content_type(self.flump_view.patch(*args, **kwargs))
