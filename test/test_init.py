from flask import Flask

from flump import FlumpView, FlumpBlueprint


def test_flump_blueprint():
    blueprint = FlumpBlueprint('test_flump', __name__)
    blueprint.register_flump_view(FlumpView(None, 'blah', '/endpoint/'))

    assert blueprint.name == 'test_flump'

    app = Flask(__name__)

    app.register_blueprint(blueprint)

    # Assert that 3 routes have been defined.
    assert len(app.url_map._rules_by_endpoint['test_flump.blah']) == 3
