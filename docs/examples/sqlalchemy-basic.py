import uuid

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flump import FlumpView, FlumpBlueprint, OrmIntegration, Fetcher
from marshmallow import fields, Schema

# Create a basic Flask app and set it to use SQLite.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/basic-test.db'

# Register the app with SQLAlchemy
db = SQLAlchemy(app)


# Instantiate our FlumpBlueprint ready for hooking up to our Flask app.
blueprint = FlumpBlueprint('flump-example', __name__)


# Define our User model
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text)
    email = db.Column(db.Text)

    # All Flump models must have an etag field.
    etag = db.Column(db.Text)


# Define our User Schema
class UserSchema(Schema):
    username = fields.Str()
    email = fields.Email()


# Define our Fetcher
class SqlALchemyFetcher(Fetcher):
    def get_many_entities(self, pagination_args):
        return User.query.all()

    def get_total_entities(self):
        return User.query.count()

    def get_entity(self, entity_id):
        return User.query.get(entity_id)


# Define our Orm Integration class
class SqlALchemyOrmIntegration(OrmIntegration):
    def delete_entity(self, entity):
        db.session.delete(entity)

    def update_entity(self, existing_entity, data):
        # Update the passed `existing_entity`.
        for k, v in data.items():
            setattr(existing_entity, k, v)

        # Ensure the etag is updated.
        existing_entity.etag = str(uuid.uuid4())
        return existing_entity

    def create_entity(self, data):
        # Note that as this is a new model it must be added to the session
        model = User(etag=str(uuid.uuid4()), **data)
        db.session.add(model)
        # We must flush the session so an ID is assigned to our Model, and we
        # can therefore return the ID.
        db.session.flush()
        return model


# Define our FlumpView class with the necessary methods overridden.
@blueprint.flump_view('/user/')
class UserView(FlumpView):
    SCHEMA = UserSchema
    RESOURCE_NAME = 'user'

    FETCHER = SqlALchemyFetcher
    ORM_INTEGRATION = SqlALchemyOrmIntegration


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
