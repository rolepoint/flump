from collections import namedtuple
from math import ceil
from werkzeug.exceptions import BadRequest

from flask import request

try:
    # handle imports for python 2/3
    from urllib.parse import urlencode, urlparse
except ImportError:
    from urllib import urlencode
    from urlparse import urlparse


PaginationArgs = namedtuple('PaginationArgs', ('page', 'size'))


class BasePagination(object):
    """
    Base Paginator class which all paginators should inherit from. Provides a
    `transform_get_many_response` function which is called from :func:`.methods.get_many.GetMany._make_get_many_response`
    in order to add any meta information as needed.
    """
    def __init__(self, fetcher):
        self.fetcher = fetcher

    def get_pagination_args(self):
        """
        Gets the pagination args from the request.
        """
        return

    def transform_get_many_response(self, response, **kwargs):
        """
        Transforms the response to a get_many request. Mainly intended to add
        extra pagination links/meta information if pagination is implemented
        for the api.

        :returns: :class:`.schemas.ManyResponseData`
        """
        return response


class PageSizePagination(BasePagination):
    """
    Mixin class which provides methods for Number/Size based pagination.
    """
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100

    def get_pagination_args(self):
        """
        Gets the pagination args from the query string.

        :returns: :class:`PaginationArgs` containing the page number and page
                  sizes specified. Accounts for
                  :attribute:`PageSizePagination.DEFAULT_PAGE_SIZE` and
                  :attribute:`PageSizePagination.MAX_PAGE_SIZE`.
        """
        page = int(request.args.get('page[number]') or 1)
        size = int(request.args.get('page[size]') or self.DEFAULT_PAGE_SIZE)

        if page < 1 or size < 1:
            raise BadRequest(
                "Both page[number] and page[size] must be at least 1"
            )

        return PaginationArgs(max(page, 1), min(size, self.MAX_PAGE_SIZE))

    def get_pagination_links(self, **kwargs):
        """
        Returns a dict containing all of the pagination links required by
        jsonapi.

        :param `**kwargs: kwargs used for constructing the pagination links.
        :returns: Dict containing the pagination links required by jsonapi.
        """
        args = self.get_pagination_args()
        total_entities = self.fetcher.get_total_entities(**kwargs)
        parsed_url = urlparse(request.url)

        other_query_params = [
            (k, v) for (k, v) in request.args.items()
            if k not in ('page[number]', 'page[size]')
        ]

        def make_url(page):
            if not total_entities:
                return None
            params = other_query_params + [
                ('page[number]', page), ('page[size]', args.size)
            ]
            return parsed_url._replace(query=urlencode(params)).geturl()

        num_pages = int(ceil(total_entities / float(args.size)))

        return {
            'self': request.url,
            'first': make_url(1),
            'last': make_url(num_pages),
            'prev': make_url(args.page - 1) if args.page > 1 else None,
            'next': make_url(args.page + 1) if args.page < num_pages else None
        }

    def transform_get_many_response(self, response, **kwargs):
        """
        Returns a `schemas.ManyResponseData` with the links replaced with
        those returned by `get_pagination_links`.

        Also adds the `max_results` and `page` args to the meta.
        """
        response = response._replace(links=self.get_pagination_links(**kwargs))
        pagination_args = self.get_pagination_args()
        meta = response.meta
        meta['extra'] = {'size': pagination_args.size,
                         'page': pagination_args.page}
        return response._replace(meta=meta)
