from flask import jsonify, request

from ..schemas import ManyResponseData, make_response_schema


class GetMany(object):
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
        pagination_args = self.paginator.get_pagination_args()
        entities = [
            self._build_entity_data(entity) for entity
            in self.fetcher.get_many_entities(pagination_args, **kwargs)
        ]

        data = self._make_get_many_response(entities, **kwargs)

        response_data, _ = self._many_response_schema(strict=True).dump(data)

        response = jsonify(response_data)
        return response, 200

    @property
    def _many_response_schema(self):
        return make_response_schema(self.SCHEMA, many=True,
                                    only=self._get_sparse_fieldset())

    def _make_get_many_response(self, entity_data, **kwargs):
        return self.paginator.transform_get_many_response(
            ManyResponseData(
                entity_data, {'self': request.url},
                {'total_count': self.fetcher.get_total_entities(**kwargs)}
            ),
            **kwargs
        )
