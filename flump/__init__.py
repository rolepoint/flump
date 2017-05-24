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
from werkzeug.exceptions import MethodNotAllowed

from .error_handlers import register_error_handlers
from .methods import HttpMethods
from .orm import OrmIntegration
from .fetcher import Fetcher
from .view import FlumpView, _FlumpMethodView
from .web_utils import MIMETYPE

__version__ = "0.10.1"

__all__ = ['FlumpView', 'FlumpBlueprint', 'OrmIntegration', 'Fetcher',
           'HttpMethods']


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
        super(FlumpBlueprint, self).__init__(*args, **kwargs)

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

    def register_flump_view(self, view_class, url):
        """
        Registers the various URL rules for the given `flump_view` on the
        Blueprint.

        :param flump_view: The :class:`.view.FlumpView` to register URLs for.
        """
        flump_view = view_class()
        view_func = _FlumpMethodView.as_view(flump_view.RESOURCE_NAME,
                                             flump_view=flump_view)
        methods = flump_view.HTTP_METHODS

        # Our canonical URLs do not have a trailing slash.
        # Though we use `strict_slashes=False` to make sure the route matches
        # on both anyway.
        url = url.rstrip('/')

        url_mapping = flump_view.URL_MAPPING

        def register_endpoint(flump_method, flask_method):
            if flump_method in url_mapping:
                func = view_func if flump_method <= methods else _meth_not_allowed
                self.add_url_rule(
                    url_mapping[flump_method].format(url), methods=flask_method,
                    view_func=func, strict_slashes=False
                )

        register_endpoint(HttpMethods.GET, ('GET', ))
        register_endpoint(HttpMethods.GET_MANY, ('GET', ))
        register_endpoint(HttpMethods.POST, ('POST', ))
        register_endpoint(HttpMethods.PATCH, ('PATCH', ))
        register_endpoint(HttpMethods.DELETE, ('DELETE', ))

    def flump_view(self, url):
        """
        A class decorator for registering a flump view.

        :param url:   The URL to register the view under.
        """
        def flump_view_decorator(view_class):
            self.register_flump_view(view_class, url)
            return view_class

        return flump_view_decorator


def _meth_not_allowed(*args, **kwargs):
    """
    We implement a function which only raises MethodNotAllowed in order to
    return the correct response for methods not defined for a given flump_view.
    """
    raise MethodNotAllowed
