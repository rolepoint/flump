from flask import current_app, url_for as flask_url_for


def url_for(*args, **kwargs):
    '''
    Override of flask url_for that correctly sets https or http based on the
    SERVER_PROTOCOL config variable.
    '''
    if kwargs.get('_external', False):
        kwargs['_scheme'] = current_app.config.get('SERVER_PROTOCOL', 'https')

    return flask_url_for(*args, **kwargs)
