from collections import namedtuple
import json
import uuid

from flask import Flask, Response
from marshmallow import fields
import pytest

from flump import FlumpView, FlumpSchema, FlumpBlueprint, MIMETYPE


User = namedtuple('User', ('id', 'etag', 'name', 'age'))


@pytest.fixture
def view_and_schema():
    instances = []

    class UserFlumpView(FlumpView):
        def get_entity(self, entity_id):
            nonlocal instances
            try:
                _id = int(entity_id)
            except ValueError:
                return

            if _id <= len(instances):
                return instances[_id - 1]

        def get_total_entities(self, **kwargs):
            nonlocal instances
            return len(instances)

        def get_many_entities(self, **kwargs):
            nonlocal instances
            return instances

        def delete_entity(self, entity):
            nonlocal instances
            instances.pop(int(entity.id) - 1)

    class UserFlumpSchema(FlumpSchema):
        name = fields.Str(required=True)
        age = fields.Integer(required=True)

        def create_entity(self, data):
            nonlocal instances
            entity = User(str(len(instances) + 1), uuid.uuid4(),
                          data['name'], data['age'])
            instances.append(entity)
            return entity

        def update_entity(self, existing_entity, data):
            return existing_entity._replace(**data)

    return UserFlumpView, UserFlumpSchema, instances


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
    flump_view = view_class(schema, 'user', '/user/')

    app = Flask(__name__)
    app.response_class = FlumpTestResponse
    app.config['SERVER_NAME'] = 'localhost'
    app.config['SERVER_PROTOCOL'] = 'http'
    app.register_blueprint(
        FlumpBlueprint('flump', __name__, flump_views=[flump_view]),
        url_prefix='/tester'
    )

    ctx = app.app_context()
    ctx.push()
    try:
        yield app
    finally:
        ctx.pop()


@pytest.fixture(scope='function')
def flask_client(app):
    return app.test_client()
