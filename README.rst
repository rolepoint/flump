Flump is a database agnostic api builder which depends on `Flask`_ and
`Marshmallow`_.

Flump tries to be as flexible as possible, giving no strong opinions/implementations
for many common API features, such as; pagination, filtering, ordering, authentication etc... Instead Flump provides easily mixed in classes which also provide a common interface for extending itself to your needs.

Marshmallow is used to provide the Schemas against which data is
validated and returned.

----------------
Getting Started
----------------

The Schema
============

You must define schemas describing your entities. These schemas should
inherit from ``FlumpSchema`` and provide methods for saving/updating the
entity.

When updating, the FlumpSchema is provided with an existing entity.

All entities used in Flump must have a field called `etag`, this should be a field
which auto updates when modified, and is used for concurrency control. For more information see :ref:`etags-design`.

When creating an entity they should also be provided with a unique identifier in
a field called `id`. For more information see :ref:`ids-design`.

For example when using Flask-SqlAlchemy ORM models you might define
something like:

.. code-block:: python

    from flask.ext.sqlalchemy import SQLAlchemy
    from marshmallow import fields
    from flump import FlumpSchema

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/basic-test.db'

    db = SQLAlchemy(app)

    class User(db.Model):
        username = db.Column(db.Text)
        email = db.Column(db.Text)
        etag = db.Column(db.Text)

    # Create the table in sqlite
    db.create_all()

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
            # Execute SQL and populate the ID field for the model
            db.session.flush()
            return model

The View
=========

We then need to hook this Schema up to a View. To do this you must provide
a View class which inherits from ``FlumpView`` and provides the following
methods:

* ``get_entity``, which retrieves a singular entity given an ``entity_id``.

* ``delete_entity``, which deletes the given instantiated ``entity``.

* ``get_many_entities``, which returns all of the entities available. If you would like to paginate the entities, we provide a mixin for this purpose. See :ref:`pagesizepagination`.

* ``get_total_entities``,  which should return a count of the total number of entities.

.. code-block:: python

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


The Blueprint
===============

To hook this into Flask you should first create a FlumpBlueprint.

.. code-block:: python

    blueprint = FlumpBlueprint(
        'flump', __name__,
        flump_views=[UserView(UserSchema, 'user', '/user/')]
    )

`FlumpBlueprint` acts like a normal Flask Blueprint, so you can register `before_request`, `after_request` & `teardown_request` handlers as usual.  For example with SQLAlchemy we either want to ``commit`` or ``rollback`` any changes
which have been made, depending on whether there has been an exception:

.. code-block:: python

    @blueprint.teardown_request
    def teardown(exception=None):
        if exception:
            db.session.rollback()
        else:
            db.session.commit()

Finally we need to hook up the blueprint to our Flask app:

.. code-block:: python

    app.register_blueprint(blueprint, url_prefix='/flump')

And you’re done!


.. _Flask: http://flask.pocoo.org
.. _Marshmallow: https://marshmallow.readthedocs.org
