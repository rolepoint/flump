# Flump

Flump is a database agnostic api builder which depends on [Flask](https://flask.pocoo.org) and [Marshmallow](https://marshmallow.readthedocs.org). 

Marshmallow is used to provide the Schemas against which data is validated and returned. The Schemas should also provide functions for updating and saving entities.

## Example Usage

You must define your schemas describing your models, these schemas must inherit from `FlumpSchema` and provide methods for saving/updating the model. 

When updating the FlumpSchema is provided with an existing model which can be accessed through `self.existing_entity`.

For example when using Flask-SqlAlchemy ORM models you might define something like:

    from flask.ext.sqlalchemy import Model, SQLAlchemy
    from marshmallow import fields
    from connect.rib.flump import FlumpSchema

    db = SQLAlchemy()

    class User(Model):
        username = db.Text()
        email = db.Text()

    class UserSchema(FlumpSchema):

        username = fields.Str()
        email = fields.Str()

        def update_entity(self, data):
            for k, v in data:
                setattr(self.existing_entity, k, v)
            return self.existing_entity

        def create_entity(self, data):
            # Note that as this is a new model it must be added to the session 
            model = User(**data)
            db.session.add(model)
            # Get an ID
            db.session.flush()
            return model

We then need to hook this Schema up to a View. To do this you must provide a View class which inherits from `FlumpView` and provides methods for `get_entity`, to retrieve a singular entity given an `entity_id`. And for `delete_entity`, to delete the given instantiated `entity`.

An example of this would be:
    
    from connect.rib.flump import FlumpSchema, FlumpView

    class UserView(FlumpView):
        def get_entity(self, entity_id):
            return User.query.get(entity_id)

        def delete_entity(self, entity):
            db.session.delete(entity)

Next you need to put all of this togther and hook it up to a Flask app. To do this you create your Blueprints using `FlumpBlueprint`.

    def setup_flump(app, db):
        from connect.rib.flump import create_api_blueprint

        blueprint = FlumpBlueprint(
            'flump', __name__,
            flump_views=[UserView(UserSchema, 'user', '/user/')]
        )

You can then define any teardown which is needed, for example with sqlalchemy we either want to `commit` or `rollback` any changes which have been made, depending on whether there has been an exception:

    @blueprint.teardown_request
    def teardown(exception=None):
        if exception:
            db.session.rollback()
        else:
            db.session.commit()

Finally we need to hook up the blueprint to our Flask app:

    app.register_blueprint(blueprint, url_prefix='/flump')

And you're done!
