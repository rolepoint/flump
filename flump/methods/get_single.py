from flask import request, jsonify

from werkzeug.exceptions import NotFound

from ..schemas import EntityData, ResponseData


class GetSingle:
    def get_single(self, entity_id, **kwargs):
        """
        Handles HTTP GET requests where a entity is specified.

        If an etag is provided and matches the current etag, returns a 304 (Not
        Modfied).

        Otherwise dumps the retrieved entity to JSON based on the current
        schema and returns it.

        :param entity_id: The entity_id used to retrieve the entity using
                          :func:`flump.view.FlumpView.get_entity`
        :param \**kwargs: Any other kwargs taken from the url which are used
                          for identifying the entity to retrieve.
        """
        entity = self.get_entity(entity_id, **kwargs)
        if not entity:
            raise NotFound

        if self._etag_matches(entity):
            return '', 304

        entity_data = EntityData(entity.id, self.RESOURCE_NAME, entity)
        response_data, _ = self.response_schema(strict=True).dump(
            ResponseData(entity_data, {'self': request.url})
        )

        response = jsonify(response_data)
        response.set_etag(str(entity.etag))
        return response, 200
