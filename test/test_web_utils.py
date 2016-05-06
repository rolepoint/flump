import json

import pytest
from werkzeug.exceptions import UnsupportedMediaType

from flump.web_utils import MIMETYPE, get_json


def run_test(app, mimetype):
    headers = {'Content-Type': mimetype}
    data = {'a': 'b'}
    json_data = json.dumps(data)
    with app.test_request_context('/user/', headers=headers, data=json_data):
        assert get_json()


@pytest.mark.parametrize("mimetype", [MIMETYPE, 'application/json', ''])
def test_get_json_works_for_expected_mimetypes(mimetype, app):
    run_test(app, mimetype)


def test_get_json_raises_for_incorrect_mimetype(app):
    with pytest.raises(UnsupportedMediaType):
        run_test(app, 'memetype')
