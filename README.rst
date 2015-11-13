Flump
=====

Flump is a database agnostic api builder which depends on `Flask`_ and
`Marshmallow`_.

Marshmallow is used to provide the Schemas against which data is
validated and returned.

Flump tries to be as flexible as possible, giving no strong opinions/implementations
for many common API features, such as; pagination, filtering, ordering, authentication etc..
Instead Flump provides easily mixed in classes which also provide a common interface for extending
itself to your needs.

Example Usage
-------------

You must define schemas describing your models. These schemas should
inherit from ``FlumpSchema`` and provide methods for saving/updating the
model.

When updating, the FlumpSchema is provided with an existing model.

For example when using Flask-SqlAlchemy ORM models you might define
something like:

.. note::

    All models used in Flump must have a field called `etag`, this should be a field
    which auto updates when modified, and is used for concurrency control.

::

    from flask.ext.sqlalchemy import Model, SQLAlchemy
    from marshmallow import fields
    from flump import FlumpSchema

    db = SQLAlchemy()

    class User(Model):
        username = db.Column(db.Text)
        email = db.Column(db.Text)
        etag = db.Column(db.Text)

    class UserSchema(FlumpSchema):

        username = fields.Str()
        email = fields.Str()

        def update_entity(self, existing_entity, data):
            for k, v in data:
                setattr(existing_entity, k, v)
            return existing_entity

        def create_entity(self, data):
            # Note that as this is a new model it must be added to the session
            model = User(**data)
            db.session.add(model)
            # Get an ID
            db.session.flush()
            return model

We then need to hook this Schema up to a View. To do this you must provide
a View class which inherits from ``FlumpView`` and provides the following
methods:

* ``get_entity``, which retrieves a singular entity given an ``entity_id``.

* ``delete_entity``, which deletes the given instantiated ``entity``.

* ``get_many_entities``, which returns all of the entities available.

* ``get_total_entities``,  which should return a count of the total number of entities.

You can limit the number of entities you wish to be
returned by using the provided ``NumberSizePagination`` mixin, or
rolling your own. The example below does NOT use the
``NumberSizePagination`` mixin.

::

    from flump import FlumpSchema, FlumpView

    class UserView(FlumpView):
        def get_many_entities(self):
            return User.query.all()

        def get_total_entities(self):
            return User.query.count()

        def get_entity(self, entity_id):
            return User.query.get(entity_id)

        def delete_entity(self, entity):
            db.session.delete(entity)

To hook this into flask you should create a FlumpBlueprint and register it with your app.

::

    def setup_flump(app, db):
        blueprint = FlumpBlueprint(
            'flump', __name__,
            flump_views=[UserView(UserSchema, 'user', '/user/')]
        )

`FlumpBlueprint` acts like a normal Flask Blueprint, so you can register `before_request`, `after_request` & `teardown_request` handlers as usual.  For example with sqlalchemy we either want to ``commit`` or ``rollback`` any changes
which have been made, depending on whether there has been an exception:

::

    @blueprint.teardown_request
    def teardown(exception=None):
        if exception:
            db.session.rollback()
        else:
            db.session.commit()

Finally we need to hook up the blueprint to our Flask app:

::

    app.register_blueprint(blueprint, url_prefix='/flump')

And you’re done!


.. _Flask: https://flask.pocoo.org
.. _Marshmallow: https://marshmallow.readthedocs.org
