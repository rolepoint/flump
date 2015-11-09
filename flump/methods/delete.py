from werkzeug.exceptions import NotFound


class Delete:

    def delete_entity(self, entity):
        """
        Should provide a method of deleting a single entity given the `entity`.
        """
        raise NotImplementedError

    def delete(self, entity_id, **kwargs):
        """
        Verifies that the etag is valid for deletion then deletes the entity
        with the given entity_id.
        """
        entity = self.get_entity(entity_id, **kwargs)
        if not entity:
            raise NotFound
        self._verify_etag(entity)
        self.delete_entity(entity)
        return '', 204
