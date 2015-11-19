from werkzeug.exceptions import NotFound


class Delete:

    def delete_entity(self, entity):
        """
        Should provide a method of deleting the `entity` passed.

        :param entity: The entity returned by
                       :func:`flump.view.FlumpView.get_entity` which is to be
                       deleted.
        """
        raise NotImplementedError

    def delete(self, entity_id, **kwargs):
        """
        Handles HTTP DELETE requests.

        Verifies that the etag is valid for deletion then deletes the entity
        with the given entity_id using
        :func:`flump.view.FlumpView.delete_entity`

        :param entity_id: The id of the entity to be deleted.
        :param \**kwargs: Any other kwargs taken from the url which are used
                          for identifying the entity to be deleted.
        """
        entity = self.get_entity(entity_id, **kwargs)
        if not entity:
            raise NotFound
        self._verify_etag(entity)
        self.delete_entity(entity)
        return '', 204
