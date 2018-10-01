import json
import os
import sys

import pytest
from flask import request

from flump import MIMETYPE
from flump.web_utils import get_json

sys.path.append(os.path.join(os.path.join(sys.path[0], 'docs'), 'examples'))
print(sys.path)
example = __import__('limited-http-methods')


@pytest.fixture(scope='module')
def client():
    example.app.testing = True
    client = example.app.test_client()
    # Make calling old flask easier
    bare_get, bare_post, bare_del, bare_patch = client.get, client.post, client.delete, client.patch
    client.get = lambda url: json.loads(bare_get(url).data.decode('utf8'))
    client.post = lambda url, data='': json.loads(bare_post(url, data=json.dumps(data), headers=[('Content-Type', MIMETYPE)]).data.decode('utf8'))
    client.patch = lambda url, data='', headers=[]: json.loads(bare_patch(url, data=json.dumps(data), headers=[('Content-Type', MIMETYPE)] + headers).data.decode('utf8'))
    return client


def test_create(client):
    assert client.post(
        '/flump/user/',
        {'data': {
            'type': 'user',
            'attributes': {
                'name': 'Carl'
            }
        }})['links'] == {
            'self': 'https://localhost/flump/user/1'
        }


def test_list(client):
    list = client.get('/flump/user/')
    del list['data'][0]['meta']
    assert list == {
        'meta': {
            'total_count': 1
        },
        'data': [{
            'attributes': {
                'name': 'Carl'
            },
            'type': 'user',
            'id': '1'
        }],
        'links': {
            'self': 'http://localhost/flump/user/'
        }
    }


def test_get(client):
    first = client.get('/flump/user/1')
    del first['data']['meta']
    assert first == {
        'data': {
            'attributes': {
                'name': 'Carl'
            },
            'type': 'user',
            'id': '1'
        },
        'links': {
            'self': 'http://localhost/flump/user/1'
        }
    }


def test_patch_fail(client):
    etag = client.get('/flump/user/1')['data']['meta']['etag']
    assert client.patch(
        '/flump/user/1', {
            'data': {
                'type': 'user',
                'attributes': {
                    'name': 'EvilCarl'
                },
                'type': 'user',
                'id': '1'
            }
        }, [('If-Match', etag)]) == {
            'message': 'The method is not allowed for the requested URL.'
        }
