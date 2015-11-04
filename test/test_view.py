from collections import namedtuple
import json
import uuid

from flask import Flask, url_for, Response
from marshmallow import fields
import pytest

from flump import FlumpView, FlumpSchema, FlumpBlueprint, MIMETYPE


User = namedtuple('User', ('id', 'etag', 'name', 'age'))


@pytest.fixture
def view_and_schema():
    instances = {}

    class UserFlumpView(FlumpView):
        def get_entity(self, entity_id):
            nonlocal instances
            return instances.get(entity_id)

        def delete_entity(self, entity):
            nonlocal instances
            instances.pop(entity.id, None)

    class UserFlumpSchema(FlumpSchema):
        name = fields.Str(required=True)
        age = fields.Integer(required=True)

        def create_entity(self, data):
            nonlocal instances
            i = len(instances) + 1
            entity = User(str(i), str(uuid.uuid4()), data['name'], data['age'])
            instances[str(i)] = entity
            return entity

        def update_entity(self, existing_entity, data):
            return existing_entity._replace(**data)

    return UserFlumpView, UserFlumpSchema


def test_flump_view_initialised_correctly(view_and_schema):
    view_class, schema = view_and_schema

    view = view_class(schema, 'blah', '/endpoint/')
    assert view.resource_schema == schema
    assert view.resource_name == 'blah'
    assert view.endpoint == '/endpoint/'


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
    view_class, schema = view_and_schema
    flump_view = view_class(schema, 'user', '/user/')

    app = Flask(__name__)
    app.response_class = FlumpTestResponse
    app.config['SERVER_NAME'] = 'localhost'
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


def _create_user(test_client, data=None):
    data = data or {
        'data': {'type': 'user', 'attributes': {'name': 'Carl', 'age': 26}}
    }
    return test_client.post(
        url_for('flump.user', _method='POST'), data=json.dumps(data),
        headers=[('Content-Type', 'application/json')]
    )


def _get_user(test_client, entity_id, etag=None):
    headers = []
    if etag:
        headers.append(('If-Match', etag))
    return test_client.get(
        url_for('flump.user', entity_id=entity_id, _method='GET'),
        headers=headers
    )


def _delete_user(test_client, entity_id, etag=None):
    url = url_for('flump.user', entity_id=entity_id, _method='DELETE')
    headers = []
    if etag:
        headers.append(('If-Match', etag))
    return test_client.delete(url, headers=headers)


def _patch_user(test_client, entity_id, data=None, etag=None):
    url = url_for('flump.user', entity_id=entity_id, _method='PATCH')
    headers = [('Content-Type', 'application/json')]
    if etag:
        headers.append(('If-Match', etag))

    data = data or {
        'data': {'type': 'user', 'id': entity_id,
                 'attributes': {'name': 'Carly', 'age': 27}}
    }

    return test_client.patch(url, data=json.dumps(data), headers=headers)


class TestPost:
    def test_post(self, flask_client):
        response = _create_user(flask_client)
        assert response.status_code == 201
        assert response.json == {
            'data': {
                'attributes': {'name': 'Carl', 'age': 26},
                'type': 'user', 'id': '1'
            },
            'links': {'self': 'https://localhost/tester/user/1'}
        }
        assert response.headers['Location'] == url_for(
            'flump.user', entity_id=response.json['data']['id'], _method='GET',
            _scheme='https'
        )
        assert response.headers['Etag']

    def test_post_fails_if_data_is_incorrect(self, flask_client):
        # data is missing a top-level 'data' key.
        data = {'type': 'user', 'attributes': {'name': 'Carl', 'age': 26}}
        response = _create_user(flask_client, data=data)
        assert response.status_code == 422

    def test_post_fails_if_attribute_is_invalid(self, flask_client):
        data = {
            'data': {'type': 'user', 'attributes': {'name': 1, 'age': 'carl'}}
        }
        response = _create_user(flask_client, data=data)
        assert response.status_code == 422
        assert response.json == {
            'errors': {
                'data': {'attributes': {'name': ['Not a valid string.'],
                                        'age': ['Not a valid integer.']}}
            },
            'message': 'JSON does not match expected schema'
        }

    def test_post_fails_if_an_id_is_specified(self, flask_client):
        data = {
            'data': {'type': 'user', 'id': '1',
                     'attributes': {'name': 'a', 'age': 26}}
        }
        response = _create_user(flask_client, data=data)
        assert response.status_code == 403

    def test_post_fails_if_wrong_resource_type_specified(self, flask_client):
        data = {
            'data': {'type': 'comment',
                     'attributes': {'name': 'Carl', 'age': 26}}
        }
        response = _create_user(flask_client, data=data)
        assert response.status_code == 409


class TestGet:
    def test_get(self, flask_client):
        user = _create_user(flask_client)
        response = _get_user(flask_client, user.json['data']['id'])
        assert response.status_code == 200
        assert response.json == {
            'data': {
                'attributes': {'name': 'Carl', 'age': 26},
                'id': '1', 'type': 'user'
            },
            'links': {'self': 'http://localhost/tester/user/1'}
        }

    def test_get_returns_not_modified_for_same_etag(self, flask_client):
        user = _create_user(flask_client)
        response = _get_user(flask_client, user.json['data']['id'])
        response = _get_user(
            flask_client, user.json['data']['id'], etag=response.headers['Etag']  # noqa
        )
        assert response.status_code == 304
        assert not response.data

    def test_get_fails_if_entity_does_not_exist(self, flask_client):
        response = _get_user(flask_client, '1')
        assert response.status_code == 404


class TestDelete:
    def test_delete(self, flask_client):
        create_response = _create_user(flask_client)
        response = _delete_user(
            flask_client, create_response.json['data']['id'],
            etag=create_response.headers['Etag']
        )

        assert response.status_code == 204
        assert not response.data

    def test_delete_works_with_wildcard_etag(self, flask_client):
        create_response = _create_user(flask_client)
        response = _delete_user(
            flask_client, create_response.json['data']['id'], etag='*'
        )

        assert response.status_code == 204
        assert not response.data

    def test_delete_fails_with_no_etag(self, flask_client):
        create_response = _create_user(flask_client)
        response = _delete_user(
            flask_client, create_response.json['data']['id']
        )

        assert response.status_code == 412

    def test_delete_fails_with_incorrect_etag(self, flask_client):
        create_response = _create_user(flask_client)
        response = _delete_user(
            flask_client, create_response.json['data']['id'], etag='wrong-etag'
        )

        assert response.status_code == 412

    def test_delete_fails_with_wrong_id(self, flask_client):
        response = _delete_user(
            flask_client, 'totallynotanid', etag='wrong-etag'
        )
        assert response.status_code == 404


class TestPatch:
    def test_patch(self, flask_client):
        create_response = _create_user(flask_client)
        response = _patch_user(
            flask_client, create_response.json['data']['id'],
            etag=create_response.headers['Etag']
        )

        assert response.status_code == 200
        assert response.json == {
            'data': {
                'attributes': {'name': 'Carly', 'age': 27},
                'id': '1', 'type': 'user'
            },
            'links': {'self': 'http://localhost/tester/user/1'}
        }

    def test_patch_updates_only_specified_field(self, flask_client):
        create_response = _create_user(flask_client)
        _id = create_response.json['data']['id']
        data = {
            'data': {
                'type': 'user', 'id': _id, 'attributes': {'name': 'Carly'}
            }
        }
        response = _patch_user(flask_client, _id, data=data,
                               etag=create_response.headers['Etag'])

        assert response.status_code == 200
        assert response.json == {
            'data': {
                'attributes': {'name': 'Carly', 'age': 26},
                'id': '1', 'type': 'user'
            },
            'links': {'self': 'http://localhost/tester/user/1'}
        }

    def test_patch_fails_without_id_field(self, flask_client):
        create_response = _create_user(flask_client)
        _id = create_response.json['data']['id']
        data = {
            'data': {'type': 'user', 'attributes': {'name': 'Carly'}}
        }
        response = _patch_user(flask_client, _id, data=data,
                               etag=create_response.headers['Etag'])

        assert response.status_code == 422

    def test_patch_works_with_wildcard_etag(self, flask_client):
        create_response = _create_user(flask_client)
        response = _patch_user(
            flask_client, create_response.json['data']['id'], etag='*'
        )

        assert response.status_code == 200
        assert response.json == {
            'data': {
                'attributes': {'name': 'Carly', 'age': 27},
                'id': '1', 'type': 'user'
            },
            'links': {'self': 'http://localhost/tester/user/1'}
        }

    def test_patch_fails_with_no_etag(self, flask_client):
        create_response = _create_user(flask_client)
        response = _patch_user(
            flask_client, create_response.json['data']['id'], etag=None
        )

        assert response.status_code == 412

    def test_patch_fails_with_incorrect_etag(self, flask_client):
        create_response = _create_user(flask_client)
        response = _patch_user(
            flask_client, create_response.json['data']['id'], etag='wrong-etag'
        )

        assert response.status_code == 412

    def test_patch_fails_with_wrong_id(self, flask_client):
        response = _patch_user(flask_client, 'notanidlol', etag='wrong-etag')

        assert response.status_code == 404
