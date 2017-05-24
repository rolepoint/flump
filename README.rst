Flump is a database agnostic api builder which depends on `Flask`_ and
`Marshmallow`_.

To get started, check out http://flump.readthedocs.io/!

Flump tries to be as flexible as possible, giving no strong
opinions/implementations for many common API features, such as; pagination,
filtering, ordering, authentication etc... Instead Flump provides easily mixed
in classes which also provide a common interface for extending itself to your
needs.

Marshmallow is used to provide the Schemas against which data is
validated and returned.

-------
Install
-------

``flump`` is on the Python Package Index (PyPI):

::

    pip install flump

----------------
Getting Started
----------------

Registering The Blueprint
===============

All the endpoints of a flump API live on a ``FlumpBlueprint``. This acts much
like a normal ``flask.Blueprint``, but provides some flump specific
functionality.

.. code-block:: python

    blueprint = FlumpBlueprint('flump', __name__)


The Schema
============

You must define schemas describing your entities. These schemas should inherit
from ``marshmallow.Schema``.

All entities used in Flump must have a field called `etag`, this should be a
field which auto updates when modified, and is used for concurrency control. For
more information see :ref:`etags-design`.

When creating an entity they should also be provided with a unique identifier in
a field called `id`. For more information see :ref:`ids-design`.

For example when using Flask-SqlAlchemy ORM models you might define something
like:

.. code-block:: python

    from flask.ext.sqlalchemy import SQLAlchemy
    from marshmallow import fields, Schema

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/basic-test.db'

    db = SQLAlchemy(app)

    class User(db.Model):
        username = db.Column(db.Text)
        email = db.Column(db.Text)
        etag = db.Column(db.Text)

    # Create the table in sqlite
    db.create_all()

    class UserSchema(Schema):

        username = fields.Str()
        email = fields.Str()

The Orm Integration
===================

In order to insert/update/delete entities we must define a class which
can talk to our database. To do this we define a class which inherits from
``flump.OrmIntegration``, and provides the following methods:

* ``delete_entity``, which deletes the given instantiated ``entity``.

* ``update_entity``, which should update the passed ``existing_entity`` and persist it in your chosen data store, then return the entity.

* ``create_entity``, which should create an entity and persist it in your chosen data store, then return the entity.

.. code-block:: python

    from flump import OrmIntegration

    class UserSqlAlchemyIntegration(OrmIntegration):
        def delete_entity(self, entity):
            db.session.delete(entity)

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


The Fetcher
===========

To get data from the database we must define a class which inherits from
``flump.Fetcher`` and provides the following methods:


* ``get_entity``, which retrieves a singular entity given an ``entity_id``.

* ``get_many_entities``, which returns all of the entities available. If you would like to paginate the entities, we provide a mixin for this purpose. See :ref:`pagination`.

* ``get_total_entities``,  which should return a count of the total number of entities.

.. code-block:: python

    from flump import Fetcher

    class UserFetcher(Fetcher):
        def get_many_entities(self):
            return User.query.all()

        def get_total_entities(self):
            return User.query.count()

        def get_entity(self, entity_id):
            return User.query.get(entity_id)


The View
=========

We can then tie these together to define our view. Our view must inherit
from ``flump.FlumpView``, and define the following properties:

* ``FETCHER``, the class we use to get entities.
* ``ORM_INTEGRATION``, the class we use to update/create/delete entities.
* ``SCHEMA``, schema which we use to marhsal/unmarshal the data.
* ``RESOURCE_NAME``, the name of the resource, used to define the URL.

.. code-block:: python

    from flump import FlumpView

    @blueprint.flump_view('/user/')
    class UserView(FlumpView):
        RESOURCE_NAME = 'user'
        SCHEMA = UserSchema
        FETCHER = UserFetcher
        ORM_INTEGRATION = UserSqlAlchemyIntegration

Registering The Blueprint
===============

`FlumpBlueprint` acts like a normal Flask Blueprint, so you can register
`before_request`, `after_request` & `teardown_request` handlers as usual. For
example with SQLAlchemy we either want to ``commit`` or ``rollback`` any changes
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
