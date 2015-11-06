def test_flump_view_initialised_correctly(view_and_schema):
    view_class, schema, _ = view_and_schema

    view = view_class(schema, 'blah', '/endpoint/')
    assert view.resource_schema == schema
    assert view.resource_name == 'blah'
    assert view.endpoint == '/endpoint/'
