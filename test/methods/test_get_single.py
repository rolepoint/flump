from mock import ANY

from ..helpers import create_user, get_user


def test_get(flask_client):
    user = create_user(flask_client)
    response = get_user(flask_client, user.json['data']['id'])
    assert response.status_code == 200
    assert response.json == {
        'data': {
            'attributes': {'name': 'Carl', 'age': 26},
            'id': '1', 'type': 'user', 'meta': {'etag': ANY}
        },
        'links': {'self': 'http://localhost/tester/user/1'}
    }


def test_get_returns_not_modified_for_same_etag(flask_client):
    user = create_user(flask_client)
    response = get_user(flask_client, user.json['data']['id'])
    response = get_user(
        flask_client, user.json['data']['id'], etag=response.headers['Etag']  # noqa
    )
    assert response.status_code == 304
    assert not response.data


def test_get_fails_if_entity_does_not_exist(flask_client):
    response = get_user(flask_client, '1')
    assert response.status_code == 404
