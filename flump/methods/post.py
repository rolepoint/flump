from flask import request, jsonify
from werkzeug.exceptions import Forbidden


from ..exceptions import FlumpUnprocessableEntity
from ..schemas import ResponseData, make_entity_schema, make_data_schema
from ..web_utils import url_for


class Post:
    @property
    def post_schema(self):
        """
        A schema describing the format of POST request for jsonapi. Provides
        automatic error checking for the data format.
        """
        data_schema = make_data_schema(self.resource_schema)
        return make_entity_schema(self.resource_schema, self.resource_name,
                                  data_schema)

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
        entity_data, errors = self.post_schema().load(self.post_data)
        if errors:
            raise FlumpUnprocessableEntity(errors=errors)

        if entity_data.id is not None:
            raise Forbidden(
                'You must not specify an id when creating an entity'
            )

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
