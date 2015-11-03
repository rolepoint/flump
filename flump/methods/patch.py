from flask import request, jsonify
from werkzeug.exceptions import NotFound

from ..exceptions import FlumpUnprocessableEntity
from ..schemas import ResponseData, make_entity_schema


class Patch:
    @property
    def patch_schema(self):
        """
        Builds a schema for PATCH requests. Passes the `entity` to the resource
        schema as the existing_entity. Also specifies the resource_schema as
        being `partial`, i.e it will ignore missing fields during
        deserialization.
        """
        return make_entity_schema(self.resource_schema, self.resource_name,
                                  only=self.patch_fields, partial=True)

    @property
    def patch_data(self):
        """
        Property so we can override in derived classes to include autogenerated
        attributes such as api_keys.
        """
        return request.json

    @property
    def patch_fields(self):
        """
        Returns the fields the user is trying to patch.
        """
        return request.json['data']['attributes'].keys()

    def patch(self, entity_id, **kwargs):
        """
        Updates an entity based on the current schema and request json. The
        schema should provide a method for updating the entity using the
        `update_entity` function.
        """
        entity = self.get_entity(entity_id, **kwargs)
        if not entity:
            raise NotFound
        self._verify_etag(entity)

        patch_schema = self.patch_schema(context={'existing_entity': entity})
        entity_data, errors = patch_schema.load(self.patch_data)
        if errors:
            raise FlumpUnprocessableEntity(errors=errors)

        data, _ = self.response_schema(strict=True).dump(
            ResponseData(entity_data, {'self': request.url})
        )

        response = jsonify(data)
        response.headers['Etag'] = entity_data.attributes.etag
        return response, 200
