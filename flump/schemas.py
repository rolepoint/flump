from collections import namedtuple

from marshmallow import Schema, fields, post_load, pre_dump
from werkzeug.exceptions import Conflict

from .exceptions import FlumpUnprocessableEntity


EntityData = namedtuple('EntityData', ('id', 'type', 'attributes'))

ResponseData = namedtuple('ResponseData', ('data', 'links'))


def make_data_schema(resource_schema, only=None, partial=False):
    """
    Constructs a Schema describing the main jsonapi format for the
    current `resource_schema`.
    """

    class JsonApiSchema(Schema):
        id = fields.Str()
        type = fields.Str(required=True)
        attributes = fields.Nested(resource_schema,
                                   required=True, only=only, partial=partial)

        @post_load
        def to_entity_data(self, data):
            """
            Automagically load the current data to the `EntityData`
            namedtuple format. When loading we do not have an ID so this
            will be None.
            """
            return EntityData(data.get('id'), data['type'], data['attributes'])

        @pre_dump
        def add_id_to_schema(self, entity_data):
            """
            Automagically take the ID from the entity_data attributes and
            return a `EntityData` instance with the given ID.
            """
            return entity_data._replace(id=entity_data.attributes.id)

    return JsonApiSchema


def make_response_schema(resource_schema, only=None):
    """
    Constructs schema describing the format of a response according to jsonapi.
    """
    data_schema = make_data_schema(resource_schema, only=only)

    class LinkSchema(Schema):
        self = fields.Str()

    class JsonApiResponseSchema(Schema):
        data = fields.Nested(data_schema)
        links = fields.Nested(LinkSchema)

    return JsonApiResponseSchema


def make_entity_schema(
    resource_schema, resource_name, only=None, partial=False
):
    """
    Constructs a schema describing the format of POST/PATCH requests for
    jsonapi. Provides automatic error checking for the data format.
    """
    data_schema = make_data_schema(resource_schema, only=only, partial=partial)

    class JsonApiPostSchema(Schema):
        data = fields.Nested(data_schema)

        @post_load
        def check_for_errors(self, loaded_data):
            """
            Checks for errors with the ID or respource type, raising the
            errors specified in jsonapi if found.
            """
            resource = loaded_data.get('data')
            if not resource:
                raise FlumpUnprocessableEntity

            if resource.type != resource_name:
                err_msg = (
                    'Url specified the creation of "{}" but type '
                    'specified "{}".'
                ).format(resource_name, resource.type)
                raise Conflict(err_msg)

            return resource

    return JsonApiPostSchema
