from mock import ANY
import pytest

from flump.web_utils import url_for
from flump.pagination import PageSizePagination

from ..helpers import create_user


class TestGetManyDefault:
    def test_get_many(self, flask_client):
        create_user(flask_client)
        create_user(flask_client)
        create_user(flask_client)

        response = flask_client.get(url_for('flump.user', _method='GET'))

        assert response.status_code == 200
        assert response.json == {
            'meta': {'total_count': 3},
            'data': [
                {
                    'attributes': {'name': 'Carl', 'age': 26},
                    'id': '1', 'type': 'user', 'meta': {'etag': ANY}
                },
                {
                    'attributes': {'name': 'Carl', 'age': 26},
                    'id': '2', 'type': 'user', 'meta': {'etag': ANY}
                },
                {
                    'attributes': {'name': 'Carl', 'age': 26},
                    'id': '3', 'type': 'user', 'meta': {'etag': ANY}
                }
            ],
            'links': {'self': 'http://localhost/tester/user/'}
        }

    def test_get_when_none_exist(self, flask_client):
        response = flask_client.get(url_for('flump.user', _method='GET'))

        assert response.status_code == 200
        assert response.json == {
            'meta': {'total_count': 0},
            'data': [],
            'links': {'self': 'http://localhost/tester/user/'}
        }


class TestGetManyWithPagination:

    @pytest.fixture
    def view_and_schema(self, view_and_schema):
        view, schema, instances = view_and_schema

        class ViewWithPagination(PageSizePagination, view):
            DEFAULT_PAGE_SIZE = 2

            def get_many_entities(self, **kwargs):
                nonlocal instances
                pagination_args = self.get_pagination_args()
                chunks = [
                    instances[i:i + pagination_args.size]
                    for i in range(0, len(instances), pagination_args.size)
                ]
                return chunks[pagination_args.page - 1]

        return ViewWithPagination, schema, instances

    def test_get_many(self, flask_client):
        create_user(flask_client)
        create_user(flask_client)
        create_user(flask_client)

        response = flask_client.get(url_for('flump.user', _method='GET'))

        base_url = 'http://localhost/tester/user/'

        assert response.status_code == 200
        assert response.json == {
            'meta': {'total_count': 3},
            'data': [
                {
                    'attributes': {'name': 'Carl', 'age': 26},
                    'id': '1', 'type': 'user', 'meta': {'etag': ANY}
                },
                {
                    'attributes': {'name': 'Carl', 'age': 26},
                    'id': '2', 'type': 'user', 'meta': {'etag': ANY}
                }
            ],
            'links': {
                'self': base_url,
                'first': base_url + '?page%5Bnumber%5D=1&page%5Bsize%5D=2',
                'last': base_url + '?page%5Bnumber%5D=2&page%5Bsize%5D=2',
                'prev': None,
                'next': base_url + '?page%5Bnumber%5D=2&page%5Bsize%5D=2',
            }
        }
        url, query_string = response.json['links']['next'].split('?')
        response = flask_client.get(url, query_string=query_string)

        assert response.status_code == 200
        assert response.json == {
            'meta': {'total_count': 3},
            'data': [
                {
                    'attributes': {'name': 'Carl', 'age': 26},
                    'id': '3', 'type': 'user', 'meta': {'etag': ANY}
                }
            ],
            'links': {
                'self': base_url + '?page[number]=2&page[size]=2',
                'first': base_url + '?page%5Bnumber%5D=1&page%5Bsize%5D=2',
                'last': base_url + '?page%5Bnumber%5D=2&page%5Bsize%5D=2',
                'next': None,
                'prev': base_url + '?page%5Bnumber%5D=1&page%5Bsize%5D=2',
            }
        }

    def test_get_many_uses_query_string(self, flask_client):
        for _ in range(10):
            create_user(flask_client)

        response = flask_client.get(
            url_for('flump.user', _method='GET'),
            query_string='page[number]=2&page[size]=3'
        )

        base_url = 'http://localhost/tester/user/'

        assert response.status_code == 200
        assert response.json == {
            'meta': {'total_count': 10},
            'data': [
                {
                    'attributes': {'name': 'Carl', 'age': 26},
                    'id': '4', 'type': 'user', 'meta': {'etag': ANY}
                },
                {
                    'attributes': {'name': 'Carl', 'age': 26},
                    'id': '5', 'type': 'user', 'meta': {'etag': ANY}
                },
                {
                    'attributes': {'name': 'Carl', 'age': 26},
                    'id': '6', 'type': 'user', 'meta': {'etag': ANY}
                }
            ],
            'links': {
                'self': base_url + '?page[number]=2&page[size]=3',
                'first': base_url + '?page%5Bnumber%5D=1&page%5Bsize%5D=3',
                'last': base_url + '?page%5Bnumber%5D=4&page%5Bsize%5D=3',
                'prev': base_url + '?page%5Bnumber%5D=1&page%5Bsize%5D=3',
                'next': base_url + '?page%5Bnumber%5D=3&page%5Bsize%5D=3'
            }
        }
