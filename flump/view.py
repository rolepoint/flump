from collections import namedtuple

from flask import jsonify, request
from flask.views import MethodView
from marshmallow import Schema, fields, post_load, pre_dump, pre_load
from werkzeug.exceptions import (
    Conflict, Forbidden, PreconditionFailed, NotFound
)
from werkzeug.exceptions import NotImplemented as WerkzeugNotImplemented


from .exceptions import FlumpUnprocessableEntity
from .web_utils import url_for


EntityData = namedtuple('EntityData', ('id', 'type', 'attributes'))

ResponseData = namedtuple('ResponseData', ('data', 'links'))


class FlumpView:
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
        parent = self

        class JsonApiSchema(Schema):
            id = fields.Str(dump_only=True)
            type = fields.Str(required=True)
            attributes = fields.Nested(parent.resource_schema, required=True,
                                       only=parent._get_sparse_fieldset())

            @pre_load
            def raise_error_if_id_provided_on_load(self, data):
                if 'id' in data:
                    raise Forbidden(
                        'You must not specify an id when creating an entity'
                    )
                return data

            @post_load
            def to_entity_data(self, data):
                """
                Automagically load the current data to the `EntityData`
                namedtuple format. When loading we do not have an ID so this
                will be None.
                """
                return EntityData(None, data['type'], data['attributes'])

            @pre_dump
            def add_id_to_schema(self, entity_data):
                """
                Automagically take the ID from the entity_data attributes and
                return a `EntityData` instance with the given ID.
                """
                return entity_data._replace(id=entity_data.attributes.id)

        return JsonApiSchema

    @property
    def response_schema(self):
        """
        A schema describing the format of a response according to jsonapi.
        """
        class LinkSchema(Schema):
            self = fields.Str()

        class JsonApiResponseSchema(Schema):
            data = fields.Nested(self.data_schema)
            links = fields.Nested(LinkSchema)

        return JsonApiResponseSchema

    @property
    def post_schema(self):
        """
        A schema describing the format of POST request for jsonapi. Provides
        automatic error checking for the data format.
        """
        parent = self

        class JsonApiPostSchema(Schema):
            data = fields.Nested(parent.data_schema)

            @post_load
            def check_for_errors(self, loaded_data):
                """
                Checks for errors with the ID or respource type, raising the
                errors specified in jsonapi if found.
                """
                resource = loaded_data.get('data')
                if not resource:
                    raise FlumpUnprocessableEntity

                if resource.type != parent.resource_name:
                    err_msg = (
                        'Url specified the creation of "{}" but type '
                        'specified "{}".'
                    ).format(parent.resource_name, resource.type)
                    raise Conflict(err_msg)

                return resource

        return JsonApiPostSchema

    def get_many(self):
        raise WerkzeugNotImplemented("Coming Soon.")

    def get_single(self, entity_id=None, **kwargs):
        """
        Gets a single instance from the entity_id using `self.get_entity`.

        If an etag is provided and matches the current etag, returns a 304 (Not
        Modfied).

        Otherwise dumps the retrieved entity to JSON based on the current
        schema and returns it.
        """
        entity = self.get_entity(entity_id, **kwargs)
        if not entity:
            raise NotFound

        if self._etag_matches(entity):
            return '', 304

        entity_data = EntityData(entity.id, self.resource_name, entity)
        response_data, _ = self.response_schema(strict=True).dump(
            ResponseData(entity_data, {'self': request.url})
        )

        response = jsonify(response_data)
        response.headers['Etag'] = entity.etag
        return response, 200

    def get(self, entity_id=None, **kwargs):
        return (
            self.get_single(entity_id, **kwargs) if entity_id
            else self.get_many()
        )

    @property
    def post_data(self):
        """
        Property so we can override in derived classes to include autogenerated
        attributes such as api_keys.
        """
        return request.json

    def post(self, **kwargs):
        """
        Creates an entity based on the current schema and request json. The
        schema should provide a method for creating the entity using the
        `create_entity` function.
        """
        entity_data, errors = self.post_schema().load(self._post_data)
        if errors:
            raise FlumpUnprocessableEntity(errors=errors)

        url = url_for('.{}'.format(self.resource_name), _external=True,
                      entity_id=entity_data.attributes.id, _method='GET',
                      **kwargs)
        data, _ = self.response_schema(strict=True).dump(
            ResponseData(entity_data, {'self': url})
        )

        response = jsonify(data)
        response.headers['Location'] = url
        response.headers['Etag'] = entity_data.attributes.etag
        return response, 201

    def delete(self, entity_id, **kwargs):
        """
        Verifies that the etag is valid for deletion then deletes the entity
        with the given entity_id.
        """
        entity = self.get_entity(entity_id, **kwargs)
        if not entity:
            raise NotFound
        self._verify_etag(entity)
        self.delete_entity(entity)
        return '', 204

    def put(self, entity_id, **kwargs):
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
        if not self._etag_matches(entity):
            raise PreconditionFailed(
                'Incorrect or missing etag in the In-Match header'
            )

    def _etag_matches(self, entity):
        """
        Returns a boolean indicating whether the etag is valid.
        """
        return request.headers.get('If-Match') in (entity.etag, '*')


class _FlumpMethodView(MethodView):
    def __init__(self, flump_view):
        self.flump_view = flump_view

    def get(self, *args, **kwargs):
        return self.flump_view.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.flump_view.post(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.flump_view.delete(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.flump_view.put(*args, **kwargs)
