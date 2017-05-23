from flask import jsonify
from werkzeug.exceptions import (Unauthorized, NotFound, Conflict,
                                 PreconditionFailed, Forbidden,
                                 MethodNotAllowed, UnsupportedMediaType,
                                 PreconditionRequired, BadRequest)

from .exceptions import FlumpUnprocessableEntity
from .web_utils import MIMETYPE


def jsonapiify(*args, **kwargs):
    response = jsonify(*args, **kwargs)
    response.headers['content-type'] = MIMETYPE
    return response


def register_error_handlers(blueprint):
    @blueprint.errorhandler(BadRequest)
    @blueprint.errorhandler(400)
    def bad_request(e):
        return jsonapiify(message=str(e.description)), 400

    @blueprint.errorhandler(Unauthorized)
    @blueprint.errorhandler(401)
    def unauthorized(e):
        return jsonapiify(message=str(e.description)), 401

    @blueprint.errorhandler(Forbidden)
    @blueprint.errorhandler(403)
    def forbidden(e):
        return jsonapiify(message=str(e.description)), 403

    @blueprint.errorhandler(NotFound)
    @blueprint.errorhandler(404)
    def page_not_found(e):
        return jsonapiify(message=str(e.description)), 404

    @blueprint.errorhandler(MethodNotAllowed)
    @blueprint.errorhandler(405)
    def method_not_allowed(e):
        return jsonapiify(message=str(e.description)), 405

    @blueprint.errorhandler(Conflict)
    @blueprint.errorhandler(409)
    def conflict(e):
        return jsonapiify(message=str(e.description)), 409

    @blueprint.errorhandler(PreconditionFailed)
    @blueprint.errorhandler(412)
    def precondition_failed(e):
        return jsonapiify(message=str(e.description)), 412

    @blueprint.errorhandler(UnsupportedMediaType)
    @blueprint.errorhandler(415)
    def unsupported_media_type(e):
        return jsonapiify(message='Unsupported media type'), 415

    @blueprint.errorhandler(FlumpUnprocessableEntity)
    @blueprint.errorhandler(422)
    def schema_validation_fail(e):
        rv = {'message': 'JSON does not match expected schema',
              'errors': e.errors}

        rv = jsonapiify(**rv)
        return rv, 422

    @blueprint.errorhandler(PreconditionRequired)
    @blueprint.errorhandler(428)
    def precondition_required(e):
        return jsonapiify(message=str(e.description)), 428
