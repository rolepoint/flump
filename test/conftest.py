from collections import namedtuple
import json
import uuid

from flask import Flask, Response
from marshmallow import fields, Schema
import pytest

from flump import FlumpView, FlumpBlueprint, MIMETYPE, OrmIntegration, Fetcher


User = namedtuple('User', ('id', 'etag', 'name', 'age'))


@pytest.fixture
def database():
    return []


@pytest.fixture
def orm_integration(database):
    class FakeOrmIntegration(OrmIntegration):
        def delete_entity(self, entity):
            database.pop(int(entity.id) - 1)

        def create_entity(self, data):
            entity = User(str(len(database) + 1), uuid.uuid4(),
                          data['name'], data['age'])
            database.append(entity)
            return entity

        def update_entity(self, existing_entity, data):
            return existing_entity._replace(**data)

    return FakeOrmIntegration


@pytest.fixture
def fetcher(database):
    class FakeFetcher(Fetcher):
        def get_entity(self, entity_id):
            try:
                _id = int(entity_id)
            except ValueError:
                return

            if _id <= len(database):
                return database[_id - 1]

        def get_total_entities(self, **kwargs):
            return len(database)

        def get_many_entities(self, pagination_args, **kwargs):
            return database

    return FakeFetcher


@pytest.fixture
def view_and_schema(fetcher, orm_integration, database):
    class UserFlumpView(FlumpView):
        RESOURCE_NAME = 'user'

        ORM_INTEGRATION = orm_integration
        FETCHER = fetcher

        class SCHEMA(Schema):
            name = fields.Str(required=True)
            age = fields.Integer(required=True)

    return UserFlumpView, UserFlumpView.SCHEMA, database


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
