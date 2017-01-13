class Fetcher(object):
    """
    Base Fetcher class. All :class:`flump.view.FlumpView` should
    have a `FETCHER` which inherits from this class and implements the
    necessary methods for their chosen HTTP methods.
    """

    def get_total_entities(self, **kwargs):
        """
        :returns: Should return an integer of the total number of entities.
        """
        raise NotImplementedError

    def get_many_entities(self, pagination_args, **kwargs):
        """
        :returns: Should return an iterable of entities.
        """
        raise NotImplementedError

    def get_entity(self, entity_id=None, **kwargs):
        """
        Should provide a method of retrieving a single entity given the
        `entity_id` and `**kwargs`.

        :param entity_id: The id of the entity to be retrieved.
        :param \**kwargs: Any other kwargs taken from the url which are used
                          for identifying the entity to be retrieved.
        :returns: The entity identified by `entity_id` and `**kwargs`.
        """
        raise NotImplementedError
