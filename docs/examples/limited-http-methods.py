import uuid
from collections import namedtuple

from flask import Flask
from flump import (FlumpBlueprint, FlumpView, HttpMethods, OrmIntegration,
                   Fetcher)
from marshmallow import Schema, fields

# Our non-persistent "database"
INSTANCES = []

# The "model" we will be storing in our "database"
User = namedtuple('User', ('id', 'etag', 'name'))


# Instantiate our FlumpBlueprint ready for hooking up to our Flask app.
blueprint = FlumpBlueprint('flump-example', __name__)


class UserSchema(Schema):
    name = fields.Str(required=True)


# Our ORM Integration, as we are not supporting DELETE or UPDATE in this
# example we do not need to include `delete_entity` or `update_entity` methods.
class FakeOrm(OrmIntegration):
    def create_entity(self, data):
        entity = User(str(len(INSTANCES) + 1), uuid.uuid4(), data['name'])
        INSTANCES.append(entity)
        return entity

    def update_entity(self, entity, data):
        return entity._replace(**data)


# Our Fetcher implementation
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


# Our FlumpView, as we are only supporing GET and POST, we specify these as
# our METHODS.
@blueprint.flump_view('/user/')
class UserView(FlumpView):
    SCHEMA = UserSchema
    RESOURCE_NAME = 'user'
    HTTP_METHODS = HttpMethods.READ_ONLY | HttpMethods.POST

    ORM_INTEGRATION = FakeOrm
    FETCHER = FakeFetcher


# Create our app and register our Blueprint
app = Flask(__name__)
app.register_blueprint(blueprint, url_prefix='/flump')


# Finally run the app.
if __name__ == "__main__":
    app.run()
