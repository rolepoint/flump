from flask import Flask
from marshmallow import fields

from flump import FlumpSchema, FlumpView, FlumpBlueprint


def test_flump_blueprint():
    blueprint = FlumpBlueprint(
        'test_flump', __name__,
        flump_views=[FlumpView(None, 'blah', '/endpoint/')]
    )

    assert blueprint.name == 'test_flump'

    app = Flask(__name__)

    app.register_blueprint(blueprint)

    # Assert that 3 routes have been defined.
    assert len(app.url_map._rules_by_endpoint['test_flump.blah']) == 3


def test_flump_schema_calls_correct_methods(mocker):
    mock_update = mocker.patch.object(FlumpSchema, 'update_entity')
    mock_create = mocker.patch.object(FlumpSchema, 'create_entity')

    class TestSchema(FlumpSchema):
        a = fields.Str()

    data = {'a': '1'}

    TestSchema().load(data)

    mock_create.assert_called_once_with(data)
    assert mock_update.call_count == 0

    TestSchema(context={'existing_entity': data}).load(data)

    mock_update.assert_called_once_with(data, data)
    assert mock_create.call_count == 1
