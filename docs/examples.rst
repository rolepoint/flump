SQlAlchemy example
====================

First off you will need to change directory to the examples directory

::

    $ cd docs/examples

You will then need to install the `sqlalchemy-requirements.txt` file to run this example:

::

    $ pip install -r sqlalchemy-requirements.txt

You can now run the code from sqlalchemy-user.py by running:

::

    $ python sqlalchemy-user.py

You now have a running CRUD API for a User model. You can query for all of the entities:

::

    $ curl http://localhost:5000/flump/user/
    {
      "data": [],
      "links": {
        "self": "http://localhost:5000/flump/user/"
      },
      "meta": {
        "total_count": 0
      }
    }

Obviously no Users exist yet, so let's create one!

::

    $ curl -XPOST http://localhost:5000/flump/user/ -H "Content-Type: application/json" -d '{"data": {"attributes": {"username": "carl", "email": "carl@rolepoint.com"}, "type": "user"}}' -i

    HTTP/1.0 201 CREATED
    Content-Type: application/vnd.api+json
    Content-Length: 210
    Location: https://localhost:5000/flump/user/1
    ETag: "0.22761545310897413"
    Server: Werkzeug/0.11 Python/3.4.2

    {
      "data": {
        "attributes": {
          "email": "carl@rolepoint.com",
          "username": "carl"
        },
        "id": "1",
        "type": "user"
      },
      "links": {
        "self": "https://localhost:5000/flump/user/1"
      }
    }

Which we can then `GET` by running

::

    $ curl http://localhost:5000/flump/user/1 -i

    HTTP/1.0 200 OK
    Content-Type: application/vnd.api+json
    Content-Length: 209
    ETag: "0.22761545310897413"
    Server: Werkzeug/0.11 Python/3.4.2
    Date: Thu, 12 Nov 2015 16:33:30 GMT

    {
      "data": {
        "attributes": {
          "email": "carl@rolepoint.com",
          "username": "carl"
        },
        "id": "1",
        "type": "user"
      },
      "links": {
        "self": "http://localhost:5000/flump/user/1"
      }
    }

We can then update our User, to do this we must provide the Etag of the User (taken from the Etag header above)

::

    $ curl -XPATCH http://localhost:5000/flump/user/1 -H "Content-Type: application/json" -d '{"data": {"attributes": {"username": "newcarl"}, "type": "user", "id": "1"}}' -H "If-Match: 0.22761545310897413"

    HTTP/1.0 200 OK
    Content-Type: application/vnd.api+json
    Content-Length: 212
    ETag: "0.10147410721726091"
    Server: Werkzeug/0.11 Python/3.4.2

    {
      "data": {
        "attributes": {
          "email": "carl@rolepoint.com",
          "username": "newcarl"
        },
        "id": "1",
        "type": "user"
      },
      "links": {
        "self": "http://localhost:5000/flump/user/1"
      }
    }

Note that the Etag in the response header has a new value.

Finally you can then delete the User:

::

    $ curl -XDELETE  http://localhost:5000/flump/user/1 -H "If-Match: 0.10147410721726091" -i

    HTTP/1.0 204 NO CONTENT
    Content-Type: application/vnd.api+json
    Content-Length: 0
    Server: Werkzeug/0.11 Python/3.4.2

