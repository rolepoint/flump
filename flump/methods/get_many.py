from flask import jsonify, request

from ..schemas import EntityData, make_response_schema, ManyResponseData


class GetMany:

    @property
    def many_response_schema(self):
        return make_response_schema(self.resource_schema, many=True,
                                    only=self._get_sparse_fieldset())

    def make_get_many_response(self, entity_data):
        return ManyResponseData(entity_data, {'self': request.url},
                                {'total_count': self.get_total_entities()})

    def get_many(self, **kwargs):
        """
        Gets many instances using `self.get_many_entities`.
        """
        data = self.make_get_many_response([
            EntityData(i.id, self.resource_name, i)
            for i in self.get_many_entities(**kwargs)
        ])

        response_data, _ = self.many_response_schema(strict=True).dump(data)

        response = jsonify(response_data)
        return response, 200
