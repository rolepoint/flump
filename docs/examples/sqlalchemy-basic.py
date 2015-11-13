import random

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flump import FlumpSchema, FlumpView, FlumpBlueprint
from marshmallow import fields

# Create a basic Flask app and set it to use SQLite.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/basic-test.db'

# Register the app with SQLAlchemy
db = SQLAlchemy(app)


# Define our User model
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    email = db.Column(db.Text)

    # All Flump models must have an etag field.
    etag = db.Column(db.Float)


# Define our User Schema
class UserSchema(FlumpSchema):
    username = fields.Str()
    email = fields.Email()

    def update_entity(self, existing_entity, data):
        # Update the passed `existing_entity`.
        for k, v in data.items():
            setattr(existing_entity, k, v)

        # Ensure the etag is updated.
        existing_entity.etag = random.random()
        return existing_entity

    def create_entity(self, data):
        # Note that as this is a new model it must be added to the session
        model = User(etag=random.random(), **data)
        db.session.add(model)
        # We must flush the session so an ID is assigned to our Model, and we
        # can therefore return the ID.
        db.session.flush()
        return model


# Define our FlumpView class with the necessary methods overridden.
class UserView(FlumpView):
    def get_many_entities(self):
        return User.query.all()

    def get_total_entities(self):
        return User.query.count()

    def get_entity(self, entity_id):
        return User.query.get(entity_id)

    def delete_entity(self, entity):
        db.session.delete(entity)


# Instantiate our FlumpBlueprint ready for hooking up to our Flask app.
blueprint = FlumpBlueprint(
    'flump-example', __name__,
    flump_views=[UserView(UserSchema, 'user', '/user/')]
)


# Define some request teardown, this is necessary to either commit, or rollback
# our changes depending on whether an exception occurred while handling the
# request.
@blueprint.teardown_request
def teardown(exception=None):
    if exception:
        db.session.rollback()
    else:
        db.session.commit()

# Register the FlumpBlueprint on our app.
app.register_blueprint(blueprint, url_prefix='/flump')

# Create our models in SQLite.
db.create_all()


# Finally run the app.
if __name__ == "__main__":
    app.run()
