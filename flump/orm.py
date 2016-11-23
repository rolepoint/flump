class OrmIntegration(object):
    """
    Base OrmIntegration class. :data:`.view.FlumpView.ORM_INTEGRATION`
    should inherit from this class and implements the necessary methods for
    the :data:`.view.FlumpView.HTTP_METHODS`.
    """
    def delete_entity(self, entity):
        """
        Should provide a method of deleting the `entity` passed.

        :param entity: The entity returned by
                       :func:`.view.FlumpView.get_entity` which is to be
                       deleted.
        """
        raise NotImplementedError

    def create_entity(self, data):
        """
        Should save an entity from the given data.

        :param data: The deserialized data dict.
        :returns: The newly created entity.
        """
        raise NotImplementedError

    def update_entity(self, existing_entity, data):
        """
        Should update an entity from the given data.

        :param existing_entity: The instance returned from
                                :func:`.view.FlumpView.get_entity`
        :param data: The deserialized data dict.
        :returns: The updated entity.
        """
        raise NotImplementedError
