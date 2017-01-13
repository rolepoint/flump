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

__version__ = "0.9.0"

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
        methods = flump_view.HTTP_METHODS

        # Our canonical URLs do not have a trailing slash.
        # Though we use `strict_slashes=False` to make sure the route matches
        # on both anyway.
        url = url.rstrip('/')

        get_many_func = (
            view_func if HttpMethods.GET_MANY < methods else _meth_not_allowed
        )
        self.add_url_rule(url, methods=('GET',),
                          view_func=get_many_func, strict_slashes=False)

        post_func = (
            view_func if HttpMethods.POST < methods else _meth_not_allowed
        )
        self.add_url_rule(url, methods=('POST',),
                          view_func=post_func, strict_slashes=False)

        all_entity_methods = (
            HttpMethods.GET | HttpMethods.PATCH | HttpMethods.DELETE
        )
        # Use the view_func for all entity specific methods which are defined
        # on the FlumpView
        entity_methods = all_entity_methods & methods
        if entity_methods:
            self.add_url_rule('{}/<entity_id>'.format(url),
                              view_func=view_func, methods=entity_methods)

        # Use the _meth_not_allowed function for all entity specific methods
        # which are not defined on the FlumpView
        not_allowed = (all_entity_methods - HttpMethods.POST -
                       HttpMethods.GET_MANY - methods)
        if not_allowed:
            self.add_url_rule('{}/<entity_id>'.format(url),
                              view_func=_meth_not_allowed, methods=not_allowed)

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
