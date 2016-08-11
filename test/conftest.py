from collections import namedtuple
import json
import uuid

from flask import Flask, Response
from marshmallow import fields, Schema
import pytest

from flump import FlumpView, FlumpBlueprint, MIMETYPE


User = namedtuple('User', ('id', 'etag', 'name', 'age'))


@pytest.fixture
def view_and_schema():
    instances = []

    class UserFlumpView(FlumpView):
        RESOURCE_NAME = 'user'

        class SCHEMA(Schema):
            name = fields.Str(required=True)
            age = fields.Integer(required=True)

        def get_entity(self, entity_id):
            try:
                _id = int(entity_id)
            except ValueError:
                return

            if _id <= len(instances):
                return instances[_id - 1]

        def get_total_entities(self, **kwargs):
            return len(instances)

        def get_many_entities(self, **kwargs):
            return instances

        def delete_entity(self, entity):
            instances.pop(int(entity.id) - 1)

        def create_entity(self, data):
            entity = User(str(len(instances) + 1), uuid.uuid4(),
                          data['name'], data['age'])
            instances.append(entity)
            return entity

        def update_entity(self, existing_entity, data):
            return existing_entity._replace(**data)

    return UserFlumpView, UserFlumpView.SCHEMA, instances


class FlumpTestResponse(Response):

    @property
    def json(self):
        '''
        Contains the decoded json from the response, if it was encoded as
        json.
        '''
        if self.content_type != MIMETYPE:
            return

        return json.loads(self.data.decode('utf-8'))


@pytest.yield_fixture
def app(view_and_schema):
    view_class, schema, _ = view_and_schema
    blueprint = FlumpBlueprint('flump', __name__)
    blueprint.register_flump_view(view_class, '/user/')

    app = Flask(__name__)
    app.response_class = FlumpTestResponse
    app.config['SERVER_NAME'] = 'localhost'
    app.config['SERVER_PROTOCOL'] = 'http'
    app.config['DEBUG'] = True
    app.config['TESTING'] = True

    app.register_blueprint(blueprint, url_prefix='/tester')

    ctx = app.app_context()
    ctx.push()
    try:
        yield app
    finally:
        ctx.pop()


@pytest.fixture(scope='function')
def flask_client(app):
    return app.test_client()
