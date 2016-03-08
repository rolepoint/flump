from flask import jsonify, request

from ..schemas import EntityData, make_response_schema, ManyResponseData


class GetMany:

    @property
    def _many_response_schema(self):
        return make_response_schema(self.SCHEMA, many=True,
                                    only=self._get_sparse_fieldset())

    def _make_get_many_response(self, entity_data, **kwargs):
        return ManyResponseData(
            entity_data, {'self': request.url},
            {'total_count': self.get_total_entities(**kwargs)}
        )

    def get_many(self, **kwargs):
        """
        Handles HTTP GET requests where no entity is specified.

        Gets many instances using
        :func:`flump.view.FlumpView.get_many_entities`, and also requires
        :func:`flump.view.FlumpView.get_total_entities` to be implemented in
        order to provide the total count.

        :param \**kwargs: kwargs taken from the url used for specifying the
                          entities to be returned.
        """
        entities = [
            EntityData(i.id, self.RESOURCE_NAME, i)
            for i in self.get_many_entities(**kwargs)
        ]
        data = self._make_get_many_response(entities, **kwargs)

        response_data, _ = self._many_response_schema(strict=True).dump(data)

        response = jsonify(response_data)
        return response, 200
