from marshmallow import fields
import pytest

from flump.validators import Immutable
from .helpers import create_user, patch_user


class TestImmutable:

    @pytest.fixture
    def view_and_schema(self, view_and_schema):
        view, schema, instances = view_and_schema

        class NotUpdateableSchema(schema):
            name = fields.Str(required=True, validate=(Immutable(),))

        return view, NotUpdateableSchema, instances

    def test_patch_does_not_allow_name_to_be_updated(self, flask_client):
        create_response = create_user(flask_client)
        response = patch_user(
            flask_client, create_response.json['data']['id'],
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
