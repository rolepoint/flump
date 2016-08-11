from collections import namedtuple
from math import ceil
try:
    from urllib.parse import urlencode, urlparse
except ImportError:
    from urllib import urlencode
    from urlparse import urlparse

from flask import request

from .web_utils import url_for


PaginationArgs = namedtuple('PaginationArgs', ('page', 'size'))


class PageSizePagination(object):
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

        return PaginationArgs(max(page, 1), min(size, self.MAX_PAGE_SIZE))

    def get_pagination_links(self, **kwargs):
        """
        Returns a dict containing all of the pagination links required by
        jsonapi.

        :param `**kwargs: kwargs used for constructing the pagination links.
        :returns: Dict containing the pagination links required by jsonapi.
        """
        args = self.get_pagination_args()
        total_entities = self.get_total_entities(**kwargs)

        parsed_url = urlparse(url_for('.{}'.format(self.RESOURCE_NAME),
                                      _external=True, _method='GET', **kwargs))
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

    def _make_get_many_response(self, entity_data, **kwargs):
        """
        Returns a `schemas.ManyResponseData` with the links replaced with
        those returned by `get_pagination_links`.

        Also adds the `max_results` and `page` args to the meta.
        """
        response = super(PageSizePagination, self)._make_get_many_response(
            entity_data, **kwargs
        )
        response = response._replace(links=self.get_pagination_links(**kwargs))
        pagination_args = self.get_pagination_args()
        meta = response.meta
        meta['extra'] = {'size': pagination_args.size,
                         'page': pagination_args.page}
        return response._replace(meta=meta)
