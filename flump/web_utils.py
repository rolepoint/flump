from flask import current_app, request, url_for as flask_url_for
from werkzeug.exceptions import UnsupportedMediaType


MIMETYPE = 'application/vnd.api+json'

ALLOWED_MIMETYPES = {MIMETYPE, 'application/json'}


def url_for(*args, **kwargs):
    '''
    Override of flask url_for that correctly sets https or http based on the
    SERVER_PROTOCOL config variable.
    '''
    if kwargs.get('_external', False):
        kwargs['_scheme'] = current_app.config.get('SERVER_PROTOCOL', 'https')

    return flask_url_for(*args, **kwargs)


def get_json():
    """
    Returns the request.json if we have the correct MIMETYPE.
    """
    if request.mimetype and request.mimetype not in ALLOWED_MIMETYPES:
        raise UnsupportedMediaType

    return request.get_json(force=True)
