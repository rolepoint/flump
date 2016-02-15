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
__version__ = "0.6.0"

import logging

from flask import Blueprint, request

from .base_view import _FlumpMethodView
from .error_handlers import register_error_handlers
from .view import FlumpView  # (imported to provide access at top level) # noqa


MIMETYPE = 'application/vnd.api+json'


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
                "and json: %s"
            )
            logger.debug(debug_string, request.method, request.view_args,
                         request.json)

        @self.after_request
        def add_mimetype(response):
            response.headers['Content-Type'] = MIMETYPE
            return response

    def register_flump_view(self, flump_view):
        """
        Registers the various URL rules for the given `flump_view` on the
        Blueprint.

        :param flump_view: The :class:`.view.FlumpView` to register URLs for.
        """
        view_func = _FlumpMethodView.as_view(flump_view.resource_name,
                                             flump_view=flump_view)

        self.add_url_rule(flump_view.endpoint,
                          methods=('GET',), view_func=view_func)
        self.add_url_rule(flump_view.endpoint, view_func=view_func,
                          methods=('POST',))
        self.add_url_rule('{}<entity_id>'.format(flump_view.endpoint),
                          view_func=view_func,
                          methods=('GET', 'PATCH', 'DELETE'))

    def register_flump_views(self, flump_views):
        """
        Registers the various URL rules for each of the the given `flump_views`
        on the Blueprint.

        :param flump_views: List of :class:`.view.FlumpView` to register URLs for.
        """
        for flump_view in flump_views:
            self.register_flump_view(flump_view)
