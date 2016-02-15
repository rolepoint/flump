from collections import namedtuple
import uuid


from flask import Flask
from flump import FlumpSchema, FlumpBlueprint
from flump.base_view import BaseFlumpView
from flump.methods.get_many import GetMany
from flump.methods.get_single import GetSingle
from flump.methods.post import Post
from marshmallow import fields

# Our non-persistent "database"
INSTANCES = []

# The "model" we will be storing in our "database"
User = namedtuple('User', ('id', 'etag', 'name'))


# Our FlumpSchema, as we are only supporing GET and POST, we don't need to
# implement the `update_entity` method.
class UserSchema(FlumpSchema):
    name = fields.Str(required=True)

    def create_entity(self, data):
        entity = User(str(len(INSTANCES) + 1), uuid.uuid4(), data['name'])
        INSTANCES.append(entity)
        return entity


# Our FlumpView, as we are only supporing GET and POST, we don't need to
# implement the `delete_entity` method. We also only inherit from the
# BaseFlumpView class, and mixin the `Get`, `GetMany` and `Post` methods.
class UserView(GetMany, GetSingle, Post, BaseFlumpView):
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


# Instantiate our FlumpBlueprint ready for hooking up to our Flask app.
blueprint = FlumpBlueprint('flump-example', __name__)
blueprint.register_flump_view(UserView(UserSchema, 'user', '/user/'))

# Create our app and register our Blueprint
app = Flask(__name__)
app.register_blueprint(blueprint, url_prefix='/flump')


# Finally run the app.
if __name__ == "__main__":
    app.run()
