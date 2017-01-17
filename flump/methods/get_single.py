from flask import jsonify, request
from werkzeug.exceptions import NotFound

from ..schemas import ResponseData


class GetSingle(object):
    def get_single(self, entity_id=None, **kwargs):
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
        entity = self.fetcher.get_entity(entity_id=entity_id, **kwargs)
        if not entity:
            raise NotFound

        if self._etag_matches(entity):
            return '', 304

        entity_data = self._build_entity_data(entity)
        response_data, _ = self.response_schema(strict=True).dump(
            ResponseData(entity_data, {'self': request.url})
        )

        response = jsonify(response_data)
        response.set_etag(str(entity_data.meta.etag))
        return response, 200
