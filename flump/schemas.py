from collections import namedtuple

from marshmallow import Schema, fields, post_load, pre_dump
from werkzeug.exceptions import Conflict

from .exceptions import FlumpUnprocessableEntity


EntityData = namedtuple('EntityData', ('id', 'type', 'attributes', 'meta'))

ResponseData = namedtuple('ResponseData', ('data', 'links'))

EntityMetaData = namedtuple('EntityMetaData', ('etag'))

ManyResponseData = namedtuple('ManyResponseData', ('data', 'links', 'meta'))


class EntityMetaSchema(Schema):
    etag = fields.Str(dump_only=True)


def make_data_schema(
    resource_schema, only=None, partial=False, id_required=False
):
    """
    Constructs a Schema describing the main jsonapi format for the
    current `resource_schema`.

    :param resource_schema: The schema describing the resource. Should be
                            an instance of :class:`marshmallow.Schema`
    :param only:            A list or tuple of fields to serialize on the
                            `resource_schema`, if None, all fields will be
                            serialized.
    :param partial:         If True, ignore missing fields on the
                            `resource_schema` when deserializing.
    :param id_required:     Whether or not the `id` field of the returned
                            `JsonApiSchema`
    :returns:               :class:`make_data_schema.JsonApiSchema`
    """

    class JsonApiSchema(Schema):
        id = fields.Str(required=id_required)
        type = fields.Str(required=True)
        attributes = fields.Nested(resource_schema,
                                   required=True, only=only, partial=partial)
        meta = fields.Nested(EntityMetaSchema, dump_only=True)

        @post_load
        def to_entity_data(self, data):
            """
            Automagically load the current data to the `EntityData`
            namedtuple format. When loading we do not have an ID so this
            will be None.
            """
            return EntityData(data.get('id'), data['type'],
                              data['attributes'], None)

    return JsonApiSchema


def make_response_schema(resource_schema, only=None, many=False):
    """
    Constructs Schema describing the format of a response according to jsonapi.

    :param resource_schema: The schema describing the resource. Should be
                            an instance of :class:`marshmallow.Schema`
    :param only:            A list or tuple of fields to serialize on the
                            `resource_schema`, if None, all fields will be
                            serialized.
    :param many:            Should be set to True if we are returning multiple
                            entities.
    :returns:               :class:`make_response_schema.JsonApiResponseSchema`
    """
    data_schema = make_data_schema(resource_schema, only=only)

    class LinkSchema(Schema):
        self = fields.Str()
        first = fields.Str()
        last = fields.Str()
        next = fields.Str()
        prev = fields.Str()

    class MetaSchema(Schema):
        total_count = fields.Integer()
        # This may contain extra data depending on the context. For instance
        # the PageSizePagination mixin makes use of this field to include the
        # current page and size in the response.
        extra = fields.Dict()

    class JsonApiResponseSchema(Schema):
        data = fields.Nested(data_schema, many=many)
        links = fields.Nested(LinkSchema)
        meta = fields.Nested(MetaSchema)

    return JsonApiResponseSchema


def make_entity_schema(resource_schema, resource_name, data_schema):
    """
    Constructs a schema describing the format of POST/PATCH requests for
    jsonapi. Provides automatic error checking for the data format.

    :param resource_schema: The schema describing the resource. Should be
                            an instance of :class:`marshmallow.Schema`
    :param resource_name:   The name of the resource type defined for the API.
    :param data_schema:     An instance or
                            :class:`make_data_schema.JsonApiSchema`.
    :returns:               :class:`make_entity_schema.JsonApiPostSchema`
    """

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
