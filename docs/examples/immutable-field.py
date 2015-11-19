from collections import namedtuple
import uuid


from flask import Flask
from flump import FlumpSchema, FlumpBlueprint, FlumpView
from flump.validators import Immutable
from marshmallow import fields

# Our non-persistent "database"
INSTANCES = []

# The "model" we will be storing in our "database"
User = namedtuple('User', ('id', 'etag', 'name', 'age'))


# Our FlumpSchema, we make the name field `Immutable`, so we cannot update it
# with a PATCH request.
class UserSchema(FlumpSchema):
    name = fields.Str(required=True, validate=(Immutable(),))
    age = fields.Integer(required=True)

    def create_entity(self, data):
        entity = User(
            str(len(INSTANCES) + 1), uuid.uuid4(), data['name'], data['age']
        )
        INSTANCES.append(entity)
        return entity

    def update_entity(self, entity, data):
        return entity._replace(**data)


# Our FlumpView, with the necessary methods implemented.
class UserView(FlumpView):
    def get_entity(self, entity_id):
        try:
            _id = int(entity_id)
        except ValueError:
            return

        if _id <= len(INSTANCES):
            return INSTANCES[_id - 1]

    def get_total_entities(self, **kwargs):
        return len(INSTANCES)

    def get_many_entities(self, **kwargs):
        return INSTANCES

    def delete_entity(self, entity_id):
        INSTANCES[int(entity_id) - 1] = None


# Instantiate our FlumpBlueprint ready for hooking up to our Flask app.
blueprint = FlumpBlueprint(
    'flump-example', __name__,
    flump_views=[UserView(UserSchema, 'user', '/user/')]
)

# Create our app and register our Blueprint
app = Flask(__name__)
app.register_blueprint(blueprint, url_prefix='/flump')


# Finally run the app.
if __name__ == "__main__":
    app.run()