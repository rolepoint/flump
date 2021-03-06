import uuid

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flump import FlumpView, FlumpBlueprint, OrmIntegration, Fetcher
from marshmallow import fields, Schema
from werkzeug.exceptions import Unauthorized
from werkzeug.security import generate_password_hash, check_password_hash

# Create a basic Flask app and set it to use SQLite.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

# Register the app with SQLAlchemy
db = SQLAlchemy(app)


# Instantiate our FlumpBlueprint ready for hooking up to our Flask app.
blueprint = FlumpBlueprint('flump-example', __name__)


# Define our User model, we include a password field which is write only,
# and a method for verifying the password. We also include an email field and
# ensure it is unique, this will allow us to use it as the identifier for our
# User when authenticating them.
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    _password = db.Column(db.Text)

    # All Flump models must have an etag field.
    etag = db.Column(db.Text)

    def __init__(self, password=None, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        if password:
            self.password = password

    @property
    def password(self):
        raise ValueError("password is write only.")

    @password.setter
    def password(self, value):
        self._password = generate_password_hash(value, method='pbkdf2:sha256')

    def verify_password(self, password):
        return check_password_hash(self._password, password)


# Define our User Schema, note that `password` is `load_only`, so we will never
# write out the password as part of our api.
class UserSchema(Schema):
    username = fields.Str()
    email = fields.Email()

    password = fields.Str(load_only=True)


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


# We need to check the auth of our user when they make any requests.
@blueprint.before_request
def check_auth(*args, **kwargs):
    # Check they have included auth
    auth = request.authorization
    if not auth:
        # Make use of flump error handling, this will return a nicely formatted
        # 401 response
        raise Unauthorized

    # Get the user with the passed in email address
    user = User.query.filter_by(email=auth.username).first()

    # If no User exists, or the password is incorrect, raise Unauthorized.
    if not (user and user.verify_password(auth.password)):
        raise Unauthorized


# Register the FlumpBlueprint on our app.
app.register_blueprint(blueprint, url_prefix='/flump')

# Create our models in SQLite.
db.create_all()

# Let's ensure there is a default User for use in this example
if not User.query.filter_by(email='test@test.com').count():
    db.session.add(User(email='test@test.com', password='password'))
    db.session.commit()


# Finally run the app.
if __name__ == "__main__":
    app.run()
