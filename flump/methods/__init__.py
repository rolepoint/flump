from .delete import Delete
from .get_many import GetMany
from .get_single import GetSingle
from .post import Post
from .patch import Patch


__all__ = ['HttpMethods', 'Delete', 'GetMany', 'GetSingle', 'Post', 'Patch']


class HttpMethods(object):
    """
    Defines the available HTTP methods for a FlumpView.

    Provides convenience sets for common api usages:
    - `ALL` allows use of all HTTP verbs for the FlumpView.
    - `READ_ONLY` allows use of only GET and GET_MANY for the FlumpView.

    When creating a FlumpView we can combine only the HTTP methods we wish to
    use, for instance to allow only GET and POST requests we would define:

    HTTP_METHODS = HttpMethods.GET | HttpMethods.POST
    """
    GET = frozenset({'GET'})
    GET_MANY = frozenset({'GET_MANY'})
    POST = frozenset({'POST'})
    PATCH = frozenset({'PATCH'})
    DELETE = frozenset({'DELETE'})

    ALL = frozenset({'GET', 'GET_MANY', 'POST', 'PATCH', 'DELETE'})
    READ_ONLY = frozenset({'GET', 'GET_MANY'})
