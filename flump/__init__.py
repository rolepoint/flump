"""
    flump
    ~~~~~
    An API builder which depends on Flask and Marshmallow and follows
    http://jsonapi.org.

    .. note:: Currently missing content negotation
             (http://jsonapi.org/format/#content-negotiation-servers), possibly
             to be added in a later version.

    :copyright: (c) 2015 by RolePoint.
"""

import logging

from flask import Blueprint, request

from .base_view import _FlumpMethodView
from .error_handlers import register_error_handlers
from .view import FlumpView
from .web_utils import MIMETYPE

__all__ = ['FlumpView', 'FlumpBlueprint']
__version__ = "0.7.5"


class FlumpBlueprint(Blueprint):
    """
    A specialised Flask Blueprint for Marshmallow, which provides a convenience
    method for registering FlumpView routes.

    Provides some default logging, which is disabled by default. This logs the
    request HTTP method, the kwargs passed to the view endpoint, and the
    request JSON body.

    Adds the 'application/vnd.api+json' Content-Type header to all responses.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        register_error_handlers(self)

        @self.before_request
        def do_logging():
            logger = logging.getLogger('flump.view.{}'.format(self.name))
            logger.propagate = False

            debug_string = (
                "%s request made for resource type %s with kwargs: %s "
                "and data: %s"
            )

            logger.debug(
                debug_string, request.method, request.view_args, request.data
            )

        @self.after_request
        def add_mimetype(response):
            response.headers['Content-Type'] = MIMETYPE
            return response

    def register_flump_view(self, view_class, url):
        """
        Registers the various URL rules for the given `flump_view` on the
        Blueprint.

        :param flump_view: The :class:`.view.FlumpView` to register URLs for.
        """
        flump_view = view_class()
        view_func = _FlumpMethodView.as_view(flump_view.RESOURCE_NAME,
                                             flump_view=flump_view)

        self.add_url_rule(url, methods=('GET',), view_func=view_func)
        self.add_url_rule(url, view_func=view_func, methods=('POST',))
        self.add_url_rule(
            '{}{}<entity_id>'.format(url, '' if url[-1] == '/' else '/'),
            view_func=view_func,
            methods=('GET', 'PATCH', 'DELETE')
        )

    def flump_view(self, url):
        """
        A class decorator for registering a flump view.

        :param url:   The URL to register the view under.
        """
        def flump_view_decorator(view_class):
            self.register_flump_view(view_class, url)
            return view_class

        return flump_view_decorator
