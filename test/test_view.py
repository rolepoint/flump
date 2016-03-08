def test_flump_view_initialised_correctly(view_and_schema):
    view_class, schema, _ = view_and_schema

    view = view_class()
    assert view.SCHEMA == schema
    assert view.RESOURCE_NAME == 'user'
