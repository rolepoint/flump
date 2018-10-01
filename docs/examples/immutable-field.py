from collections import namedtuple
import uuid

from flask import Flask
from flump import FlumpBlueprint, FlumpView, OrmIntegration, Fetcher
from flump.validators import Immutable
from marshmallow import fields, Schema

# Our non-persistent "database"
INSTANCES = []

# The "model" we will be storing in our "database"
User = namedtuple('User', ('id', 'etag', 'name', 'age'))


# Instantiate our FlumpBlueprint ready for hooking up to our Flask app.
blueprint = FlumpBlueprint('flump-example', __name__)


# Our Schema, we make the name field `Immutable`, so we cannot update it
# with a PATCH request.
class UserSchema(Schema):
    name = fields.Str(required=True, validate=(Immutable(),))
    age = fields.Integer(required=True)


# Our ORM Integration
class FakeOrm(OrmIntegration):
    def delete_entity(self, entity):
        INSTANCES[int(entity.id) - 1] = None

    def create_entity(self, data):
        entity = User(
            str(len(INSTANCES) + 1), uuid.uuid4(), data['name'], data['age']
        )
        INSTANCES.append(entity)
        return entity

    def update_entity(self, entity, data):
        return entity._replace(**data)


# Our Fetcher
class FakeFetcher(Fetcher):
    def get_entity(self, entity_id):
        try:
            _id = int(entity_id)
        except ValueError:
            return

        if _id <= len(INSTANCES):
            return INSTANCES[_id - 1]

    def get_total_entities(self, **kwargs):
        return len(INSTANCES)

    def get_many_entities(self, pagination_args, **kwargs):
        return INSTANCES


@blueprint.flump_view('/user/')
class UserView(FlumpView):
    SCHEMA = UserSchema
    RESOURCE_NAME = 'user'

    ORM_INTEGRATION = FakeOrm
    FETCHER = FakeFetcher


# Create our app and register our Blueprint
app = Flask(__name__)
app.register_blueprint(blueprint, url_prefix='/flump')


# Finally run the app.
if __name__ == "__main__":
    app.run()
