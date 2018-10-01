import base64
import json
import os
import sys

import pytest
from flask import request

from flump import MIMETYPE
from flump.web_utils import get_json

sys.path.append(os.path.join(os.path.join(sys.path[0], 'docs'), 'examples'))
print(sys.path)
example = __import__('sqlalchemy-auth')


@pytest.fixture(scope='module')
def client():
    example.app.testing = True
    client = example.app.test_client()
    # Make calling old flask easier
    bare_get, bare_post, bare_del, bare_patch = client.get, client.post, client.delete, client.patch
    client.get = lambda url, headers: json.loads(bare_get(url, headers=headers).data.decode('utf8'))
    client.post = lambda url, data='', headers=[]: json.loads(bare_post(url, data=json.dumps(data), headers=[('Content-Type', MIMETYPE)] + headers).data.decode('utf8'))
    client.delete = lambda url, headers=[]: bare_del(url, headers=headers).data.decode('utf8')
    client.patch = lambda url, data='', headers=[]: json.loads(bare_patch(url, data=json.dumps(data), headers=[('Content-Type', MIMETYPE)] + headers).data.decode('utf8'))
    return client


@pytest.fixture
def auth():
    return ('Authorization',
            b"Basic " + base64.b64encode(b"test@test.com:password"))


def test_create(client, auth):
    assert client.post(
        '/flump/user/', {
            'data': {
                'type': 'user',
                'attributes': {
                    'email': 'Carl@example.com',
                    'password': 'Password123'
                }
            }
        }, [auth])['links'] == {
            'self': 'https://localhost/flump/user/2'
        }


def test_list(client, auth):
    assert client.get('/flump/user/', [auth])["meta"]["total_count"] == 2


def test_list_no_auth(client, auth):
    assert client.get('/flump/user/', []) == {
        'message':
        "The server could not verify that you are authorized to access the URL requested.  You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."
    }


def test_get(client, auth):
    first = client.get('/flump/user/1', [auth])
    del first['data']['meta']
    assert first == {
        'data': {
            'attributes': {
                'email': 'test@test.com'
            },
            'type': 'user',
            'id': '1'
        },
        'links': {
            'self': 'http://localhost/flump/user/1'
        }
    }


def test_patch(client, auth):
    etag = client.get('/flump/user/2', [auth])['data']['meta']['etag']
    assert client.patch(
        '/flump/user/2', {
            'data': {
                'type': 'user',
                'attributes': {
                    'password': 'newpassword'
                },
                'type': 'user',
                'id': '2'
            }
        }, [('If-Match', etag), auth])['links'] == {
            'self': 'http://localhost/flump/user/2'
        }


def test_delete_user(client, auth):
    etag = client.get('/flump/user/2', [auth])['data']['meta']['etag']
    client.delete('/flump/user/2', [('If-Match', etag), auth])
