from .base_view import BaseFlumpView
from .methods import Patch, Delete, GetMany, GetSingle, Post


class FlumpView(Patch, Delete, GetMany, GetSingle, Post, BaseFlumpView):
    """
    Implements Flump views using the HTTP method mixins.

    Provides `GET` single and many entities, `PATCH`, `POST` and `DELETE`
    endpoints.

    If a client wishes to provide an API without any of the usual HTTP methods,
    they can inherit from BaseFlumpView, and mixin whichever HTTP methods they
    prefer.

    View classes which inherit from this must provide the following methods:

    * ``get_entity``, which retrieves a singular entity given an ``entity_id``.

    * ``delete_entity``, which deletes the given instantiated ``entity``.

    * ``get_many_entities``, which returns all of the entities available.

    * ``get_total_entities``,  which should return a count of the total number of entities.

    :param resource_schema: The schema describing the resource. Should be
                            an instance of :class:`flump.FlumpSchema`
    :param resource_name:   The name of the resource type the API will be
                            used for.
    :param endpoint:        The URL endpoint the API should live at.
    """
