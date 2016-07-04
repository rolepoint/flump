import json

from flump.web_utils import url_for
from mock import ANY

from ..helpers import create_user


def test_post(flask_client):
    response = create_user(flask_client)
    assert response.status_code == 201
    assert response.json == {
        'data': {
            'attributes': {'name': 'Carl', 'age': 26},
            'type': 'user', 'id': '1', 'meta': {'etag': ANY}
        },
        'links': {'self': 'http://localhost/tester/user/1'}
    }
    assert response.headers['Location'] == url_for(
        'flump.user', entity_id=response.json['data']['id'], _method='GET',
        _scheme='http'
    )
    assert response.headers['Etag']


def test_post_works_with_json_mimetype(flask_client):
    response = create_user(flask_client, mimetype='application/json')
    assert response.status_code == 201


def test_post_fails_if_data_is_incorrect(flask_client):
    # data is missing a top-level 'data' key.
    data = {'type': 'user', 'attributes': {'name': 'Carl', 'age': 26}}
    response = create_user(flask_client, data=data)
    assert response.status_code == 422


def test_post_fails_if_attribute_is_invalid(flask_client):
    data = {
        'data': {'type': 'user', 'attributes': {'name': 1, 'age': 'carl'}}
    }
    response = create_user(flask_client, data=data)
    assert response.status_code == 422
    assert response.json == {
        'errors': {
            'data': {'attributes': {'name': ['Not a valid string.'],
                                    'age': ['Not a valid integer.']}}
        },
        'message': 'JSON does not match expected schema'
    }


def test_post_fails_if_an_id_is_specified(flask_client):
    data = {
        'data': {'type': 'user', 'id': '1',
                 'attributes': {'name': 'a', 'age': 26}}
    }
    response = create_user(flask_client, data=data)
    assert response.status_code == 403


def test_post_fails_if_wrong_resource_type_specified(flask_client):
    data = {
        'data': {'type': 'comment',
                 'attributes': {'name': 'Carl', 'age': 26}}
    }
    response = create_user(flask_client, data=data)
    assert response.status_code == 409



def test_post_fails_if_wrong_content_type_used(flask_client):
    response = create_user(flask_client, mimetype='bad_mimetype')
    assert response.status_code == 415


def test_no_redirect_with_trailing_slash(flask_client):
    data = {
        'data': {'type': 'user', 'attributes': {'name': 'Carl', 'age': 26}}
    }
    url = url_for('flump.user', _method='POST')
    assert url[-1] != '/'
    url = url + '/'
    response = flask_client.post(
        url, data=json.dumps(data),
        headers=[('Content-Type', 'application/json')]
    )
    assert response.status_code == 201
