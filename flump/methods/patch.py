from flask import request, jsonify
from werkzeug.exceptions import NotFound

from ..exceptions import FlumpUnprocessableEntity
from ..schemas import ResponseData, make_entity_schema, make_data_schema


class Patch:
    @property
    def _patch_schema(self):
        """
        Builds a schema for PATCH requests. Specifies the resource_schema as
        being `partial`, i.e it will ignore missing fields during
        deserialization.
        """
        fields = request.json['data']['attributes'].keys()
        return make_entity_schema(
            self.resource_schema, self.resource_name,
            make_data_schema(
                self.resource_schema, id_required=True,
                only=fields, partial=True
            )
        )

    @property
    def patch_data(self):
        """
        Property so we can override in derived classes to include autogenerated
        attributes such as api_keys.
        """
        return request.json

    def patch(self, entity_id, **kwargs):
        """
        Handles HTTP PATCH requests.

        Updates an entity based on the current schema and request json. The
        schema should provide a method for updating the entity using
        :func:`flump.FlumpSchema.update_entity`.

        :param entity_id: The entity_id used to retrieve the entity using
                          :func:`flump.view.FlumpView.get_entity`
        :param \**kwargs: Any other kwargs taken from the url which are used
                          for identifying the entity to patch.
        """
        entity = self.get_entity(entity_id, **kwargs)
        if not entity:
            raise NotFound
        self._verify_etag(entity)

        patch_schema = self._patch_schema(context={'existing_entity': entity})
        entity_data, errors = patch_schema.load(self.patch_data)
        if errors:
            raise FlumpUnprocessableEntity(errors=errors)

        data, _ = self.response_schema(strict=True).dump(
            ResponseData(entity_data, {'self': request.url})
        )

        response = jsonify(data)
        response.set_etag(str(entity.etag))
        return response, 200
