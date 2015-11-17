from collections import namedtuple
from math import ceil
from urllib.parse import urlencode, urlparse

from flask import request

from .web_utils import url_for


PaginationArgs = namedtuple('PaginationArgs', ('page', 'size'))


class PageSizePagination:
    """
    Mixin class which provides methods for Number/Size based pagination.
    """
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 20

    def get_pagination_args(self):
        """
        Returns the pagination args, accounting for defaults and maximums.
        """
        page = int(request.args.get('page[number]') or 1)
        size = int(request.args.get('page[size]') or self.DEFAULT_PAGE_SIZE)

        return PaginationArgs(max(page, 1), min(size, self.MAX_PAGE_SIZE))

    def get_pagination_links(self, **kwargs):
        """
        Returns a dict containing all of the pagination links required by
        jsonapi.
        """
        args = self.get_pagination_args()
        total_entities = self.get_total_entities(**kwargs)

        parsed_url = urlparse(url_for('.{}'.format(self.resource_name),
                                      _external=True, _method='GET', **kwargs))

        def make_url(page):
            if not total_entities:
                return None
            params = (('page[number]', page), ('page[size]', args.size))
            return parsed_url._replace(query=urlencode(params)).geturl()

        num_pages = int(ceil(total_entities / float(args.size)))

        return {
            'self': request.url,
            'first': make_url(1),
            'last': make_url(num_pages),
            'prev': make_url(args.page - 1) if args.page > 1 else None,
            'next': make_url(args.page + 1) if args.page < num_pages else None
        }

    def make_get_many_response(self, entity_data, **kwargs):
        """
        Returns a `schemas.ManyResponseData` with the links replaced with
        those returned by `get_pagination_links`.
        """
        response = super().make_get_many_response(entity_data, **kwargs)
        return response._replace(links=self.get_pagination_links(**kwargs))