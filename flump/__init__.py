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
__version__ = "0.4.0"

import logging

from flask import Blueprint, request
from marshmallow import Schema, post_load

from .base_view import _FlumpMethodView
from .error_handlers import register_error_handlers
from .view import FlumpView  # (imported to provide access at top level) # noqa


MIMETYPE = 'application/vnd.api+json'


class FlumpBlueprint(Blueprint):
    """
    Exactly the same as a Flask Blueprint, but provides a convenience method
    for registering FlumpView routes.

    Also provides some default logging, and adds the 'application/vnd.api+json'
    Content-Type header to all responses.

    :param flump_views: A list of :class:`.view.FlumpView`
    """
    def __init__(self, *args, flump_views=None, **kwargs):
        super().__init__(*args, **kwargs)

        for view in (flump_views or []):
            self.register_flump_view(view)

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


class FlumpSchema(Schema):
    """
    The basic Schema which all `FlumpView.base_schema` should be an instance
    of.

    Provides automatic entity creation/updating through the `post_load` hook.

    Classes inheriting from this MUST provide `update_entity` and
    `create_entity` methods to create/update entities.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @post_load
    def handle_entity(self, data):
        existing_entity = self.context.get('existing_entity')
        if existing_entity:
            return self.update_entity(existing_entity, data)

        return self.create_entity(data)

    def update_entity(self, existing_entity, data):
        """
        Should update an entity from the given data.

        :param existing_entity: The instance returned from
                                :func:`.view.FlumpView.get_entity`
        :param data: Dict whose key/values correspond to the schema attributes
                     after being loaded.
        """
        raise NotImplementedError

    def create_entity(self, data):
        """
        Should save an entity from the given data.

        :param data: Dict whose key/values correspond to the schema attributes
                     after being loaded.
        """
        raise NotImplementedError
