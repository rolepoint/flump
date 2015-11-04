from flask import jsonify
from werkzeug.exceptions import (Unauthorized, NotFound, Conflict,
                                 PreconditionFailed, Forbidden,
                                 NotImplemented, UnsupportedMediaType,
                                 PreconditionRequired)

from .exceptions import FlumpUnprocessableEntity


def register_error_handlers(blueprint):

    @blueprint.errorhandler(Unauthorized)
    @blueprint.errorhandler(401)
    def unauthorized(e):
        return jsonify(message=str(e.description)), 401

    @blueprint.errorhandler(Forbidden)
    @blueprint.errorhandler(403)
    def forbidden(e):
        return jsonify(message=str(e.description)), 403

    @blueprint.errorhandler(NotFound)
    @blueprint.errorhandler(404)
    def page_not_found(e):
        return jsonify(message=str(e.description)), 404

    @blueprint.errorhandler(Conflict)
    @blueprint.errorhandler(409)
    def conflict(e):
        return jsonify(message=str(e.description)), 409

    @blueprint.errorhandler(PreconditionFailed)
    @blueprint.errorhandler(412)
    def precondition_failed(e):
        return jsonify(message=str(e.description)), 412

    @blueprint.errorhandler(UnsupportedMediaType)
    @blueprint.errorhandler(415)
    def unsupported_media_type(e):
        return jsonify(message='Unsupported media type'), 415

    @blueprint.errorhandler(FlumpUnprocessableEntity)
    @blueprint.errorhandler(422)
    def schema_validation_fail(e):
        rv = {'message': 'JSON does not match expected schema',
              'errors': e.errors}

        rv = jsonify(**rv)
        return rv, 422

    @blueprint.errorhandler(PreconditionRequired)
    @blueprint.errorhandler(428)
    def precondition_required(e):
        return jsonify(message=str(e.description)), 428

    @blueprint.errorhandler(NotImplemented)
    @blueprint.errorhandler(501)
    def not_implemented(e):
        return jsonify(message=str(e.description)), 501
