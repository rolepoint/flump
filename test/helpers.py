import json

from flump import MIMETYPE
from flump.web_utils import url_for


def create_user(test_client, data=None, mimetype=MIMETYPE):
    data = data or {
        'data': {'type': 'user', 'attributes': {'name': 'Carl', 'age': 26}}
    }
    return test_client.post(
        url_for('flump.user', _method='POST'), data=json.dumps(data),
        headers=[('Content-Type', mimetype)]
    )


def get_user(test_client, entity_id, etag=None):
    headers = []
    if etag:
        headers.append(('If-Match', etag))
    return test_client.get(
        url_for('flump.user', entity_id=entity_id, _method='GET'),
        headers=headers
    )


def delete_user(test_client, entity_id, etag=None):
    url = url_for('flump.user', entity_id=entity_id, _method='DELETE')
    headers = []
    if etag:
        headers.append(('If-Match', etag))
    return test_client.delete(url, headers=headers)


def patch_user(test_client, entity_id, data=None, etag=None, mimetype=MIMETYPE):
    url = url_for('flump.user', entity_id=entity_id, _method='PATCH')
    headers = [('Content-Type', mimetype)]
    if etag:
        headers.append(('If-Match', etag))

    data = data or {
        'data': {'type': 'user', 'id': entity_id,
                 'attributes': {'name': 'Carly', 'age': 27}}
    }

    return test_client.patch(url, data=json.dumps(data), headers=headers)
