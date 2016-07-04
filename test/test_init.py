from flask import Flask

from flump import FlumpView, FlumpBlueprint


class ViewForTest(FlumpView):
    RESOURCE_NAME = 'blah'
    SCHEMA = None


def test_flump_blueprint():
    blueprint = FlumpBlueprint('test_flump', __name__)
    blueprint.register_flump_view(ViewForTest, '/endpoint/')

    assert blueprint.name == 'test_flump'

    app = Flask(__name__)

    app.register_blueprint(blueprint)

    rules = [i.rule for i in app.url_map._rules_by_endpoint['test_flump.blah']]
    assert rules == ['/endpoint', '/endpoint', '/endpoint/<entity_id>']


def test_flump_view_decorator():
    blueprint = FlumpBlueprint('test_flump', __name__)

    @blueprint.flump_view('/endpoint/')
    class View(ViewForTest):
        pass

    app = Flask(__name__)
    app.register_blueprint(blueprint)

    # Assert that 3 routes have been defined.
    rules = [i.rule for i in app.url_map._rules_by_endpoint['test_flump.blah']]
    assert rules == ['/endpoint', '/endpoint', '/endpoint/<entity_id>']


def test_adds_trailing_slash_to_id_specific_route_if_left_off():
    blueprint = FlumpBlueprint('test_flump', __name__)
    blueprint.register_flump_view(ViewForTest, '/endpoint')

    assert blueprint.name == 'test_flump'

    app = Flask(__name__)

    app.register_blueprint(blueprint)

    rules = [i.rule for i in app.url_map._rules_by_endpoint['test_flump.blah']]
    assert rules == ['/endpoint', '/endpoint', '/endpoint/<entity_id>']
