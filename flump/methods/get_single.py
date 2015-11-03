from flask import request, jsonify

from werkzeug.exceptions import NotFound

from ..schemas import EntityData, ResponseData


class GetSingle:
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
