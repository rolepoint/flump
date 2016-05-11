from marshmallow import fields
from mock import ANY
import pytest

from flump.validators import Immutable
from .helpers import create_user, patch_user


class TestImmutable:

    @pytest.fixture
    def view_and_schema(self, view_and_schema):
        view, schema, instances = view_and_schema

        class NotUpdateableSchema(schema):
            name = fields.Str(required=True, validate=(Immutable(),))

        view.SCHEMA = NotUpdateableSchema

        return view, NotUpdateableSchema, instances

    def test_patch_does_not_allow_name_to_be_updated(self, flask_client):
        create_response = create_user(flask_client)
        _id = create_response.json['data']['id']
        response = patch_user(
            flask_client, _id,
            etag=create_response.headers['Etag']
        )
        assert response.status_code == 422
        assert response.json == {
            'errors': {
                'data': {
                    'attributes': {
                        'name': ["Can't update immutable fields."]
                    }
                }
            },
            'message': 'JSON does not match expected schema'
        }

    def test_patch_does_not_enforce_name_being_present(self, flask_client):
        create_response = create_user(flask_client)
        _id = create_response.json['data']['id']
        response = patch_user(
            flask_client, _id,
            etag=create_response.headers['Etag'],
            data={'data': {'type': 'user', 'id': _id,
                           'attributes': {'age': 99}}}
        )
        assert response.status_code == 200
        assert response.json == {
            'data': {
                'attributes': {'age': 99, 'name': 'Carl'},
                'id': '1',
                'type': 'user',
                'meta': {'etag': ANY}
            },
            'links': {'self': 'http://localhost/tester/user/1'}
        }

    def test_can_print_immutable(self):
        # A wierd test to have, but I was getting exceptions messing about
        # with things from the repl.
        print(Immutable())
