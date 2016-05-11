from mock import ANY

from ..helpers import create_user, patch_user


def test_patch(flask_client):
    create_response = create_user(flask_client)
    response = patch_user(
        flask_client, create_response.json['data']['id'],
        etag=create_response.headers['Etag']
    )

    assert response.status_code == 200
    assert response.json == {
        'data': {
            'attributes': {'name': 'Carly', 'age': 27},
            'id': '1', 'type': 'user', 'meta': {'etag': ANY}
        },
        'links': {'self': 'http://localhost/tester/user/1'}
    }


def test_patch_works_with_json_mimetype(flask_client):
    mimetype = 'application/json'
    create_response = create_user(flask_client, mimetype=mimetype)
    response = patch_user(
        flask_client, create_response.json['data']['id'],
        etag=create_response.headers['Etag'], mimetype=mimetype
    )

    assert response.status_code == 200


def test_patch_updates_only_specified_field(flask_client):
    create_response = create_user(flask_client)
    _id = create_response.json['data']['id']
    data = {
        'data': {
            'type': 'user', 'id': _id, 'attributes': {'name': 'Carly'}
        }
    }
    response = patch_user(flask_client, _id, data=data,
                          etag=create_response.headers['Etag'])

    assert response.status_code == 200
    assert response.json == {
        'data': {
            'attributes': {'name': 'Carly', 'age': 26},
            'id': '1', 'type': 'user', 'meta': {'etag': ANY}
        },
        'links': {'self': 'http://localhost/tester/user/1'}
    }


def test_patch_fails_without_id_field(flask_client):
    create_response = create_user(flask_client)
    _id = create_response.json['data']['id']
    data = {
        'data': {'type': 'user', 'attributes': {'name': 'Carly'}}
    }
    response = patch_user(flask_client, _id, data=data,
                          etag=create_response.headers['Etag'])

    assert response.status_code == 422


def test_patch_works_with_wildcard_etag(flask_client):
    create_response = create_user(flask_client)
    response = patch_user(
        flask_client, create_response.json['data']['id'], etag='*'
    )

    assert response.status_code == 200
    assert response.json == {
        'data': {
            'attributes': {'name': 'Carly', 'age': 27},
            'id': '1', 'type': 'user', 'meta': {'etag': ANY}
        },
        'links': {'self': 'http://localhost/tester/user/1'}
    }


def test_patch_fails_with_no_etag(flask_client):
    create_response = create_user(flask_client)
    response = patch_user(
        flask_client, create_response.json['data']['id'], etag=None
    )

    assert response.status_code == 428


def test_patch_fails_with_incorrect_etag(flask_client):
    create_response = create_user(flask_client)
    response = patch_user(
        flask_client, create_response.json['data']['id'], etag='wrong-etag'
    )

    assert response.status_code == 412


def test_patch_fails_with_wrong_id(flask_client):
    response = patch_user(flask_client, 'notanidlol', etag='wrong-etag')

    assert response.status_code == 404


def test_patch_fails_with_bad_content_type(flask_client):
    create_response = create_user(flask_client)
    response = patch_user(
        flask_client, create_response.json['data']['id'],
        etag=create_response.headers['Etag'], mimetype='bad_mimetype'
    )

    assert response.status_code == 415
