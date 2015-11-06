from ..helpers import create_user, delete_user


def test_delete(flask_client):
    create_response = create_user(flask_client)
    response = delete_user(
        flask_client, create_response.json['data']['id'],
        etag=create_response.headers['Etag']
    )

    assert response.status_code == 204
    assert not response.data


def test_delete_works_with_wildcard_etag(flask_client):
    create_response = create_user(flask_client)
    response = delete_user(
        flask_client, create_response.json['data']['id'], etag='*'
    )

    assert response.status_code == 204
    assert not response.data


def test_delete_fails_with_no_etag(flask_client):
    create_response = create_user(flask_client)
    response = delete_user(
        flask_client, create_response.json['data']['id']
    )

    assert response.status_code == 428


def test_delete_fails_with_incorrect_etag(flask_client):
    create_response = create_user(flask_client)
    response = delete_user(
        flask_client, create_response.json['data']['id'], etag='wrong-etag'
    )

    assert response.status_code == 412


def test_delete_fails_with_wrong_id(flask_client):
    response = delete_user(
        flask_client, 'totallynotanid', etag='wrong-etag'
    )
    assert response.status_code == 404
