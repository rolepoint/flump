Simple SQlAlchemy example
====================

Before reading through this example, we recommend reading through :ref:`sqlalchemy-basic`.

First off you will need to change directory to the examples directory

.. code-block.. code-block:: guess guess

    $ cd docs/examples

You will then need to install the `sqlalchemy-requirements.txt` file to run this example:

.. code-block:: guess

    $ pip install -r sqlalchemy-requirements.txt

You can now run the code from sqlalchemy-basic.py by running:

.. code-block:: guess

    $ python sqlalchemy-basic.py

You now have a running CRUD API for a User entity. You can query for all of the entities:

.. code-block:: guess

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

.. code-block:: guess

    $ curl -XPOST http://localhost:5000/flump/user/ -H "Content-Type: application/json" -d '{"data": {"attributes": {"username": "carl", "email": "carl@rolepoint.com"}, "type": "user"}}' -i

    HTTP/1.0 201 CREATED
    Content-Type: application/vnd.api+json
    Content-Length: 210
    Location: https://localhost:5000/flump/user/1
    ETag: "32fc216a-f385-4fbc-9404-9ba44ea4e8eb"
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

.. code-block:: guess

    $ curl http://localhost:5000/flump/user/1 -i

    HTTP/1.0 200 OK
    Content-Type: application/vnd.api+json
    Content-Length: 209
    ETag: "32fc216a-f385-4fbc-9404-9ba44ea4e8eb"
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

.. code-block:: guess

    $ curl -XPATCH http://localhost:5000/flump/user/1 -H "Content-Type: application/json" -d '{"data": {"attributes": {"username": "newcarl"}, "type": "user", "id": "1"}}' -H "If-Match: 32fc216a-f385-4fbc-9404-9ba44ea4e8eb"

    HTTP/1.0 200 OK
    Content-Type: application/vnd.api+json
    Content-Length: 212
    ETag: "cd5d56b0-a3bb-4d13-8f39-46b20b0580d2"
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

.. code-block:: guess

    $ curl -XDELETE  http://localhost:5000/flump/user/1 -H "If-Match: cd5d56b0-a3bb-4d13-8f39-46b20b0580d2" -i

    HTTP/1.0 204 NO CONTENT
    Content-Type: application/vnd.api+json
    Content-Length: 0
    Server: Werkzeug/0.11 Python/3.4.2

.. _basic-auth-example:

SQLAlchemy Example with Basic Auth
==============================

Before reading through this example, we recommend reading through :ref:`sqlalchemy-auth`.

Our first example was very simple, and we can now show how easily extensible Flump is by adding some basic
authentication to our API.

As with the basic example above, you will first need to change directory to the examples directory

.. code-block:: guess

    $ cd docs/examples

You will then need to install the `sqlalchemy-requirements.txt` file to run this example:

.. code-block:: guess

    $ pip install -r sqlalchemy-requirements.txt

You can now run the code from sqlalchemy-auth.py by running:

.. code-block:: guess

    $ python sqlalchemy-auth.py

We now have an API with Basic Authentication running on `http://localhost:5000`, we can verify this
with the following `curl` command:

.. code-block:: guess

    $ curl http://localhost:5000/flump/user/ -i

      HTTP/1.0 401 UNAUTHORIZED
      Content-Type: application/vnd.api+json
      Content-Length: 240
      Server: Werkzeug/0.11.2 Python/3.4.2
      Date: Fri, 13 Nov 2015 12:47:06 GMT

      {
        "message": "The server could not verify that you are authorized to access the URL requested.  You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required."
      }

As shown in the response, we have not authenticated. The `sqlalchemy-auth.py` file has helpfully created a User for us, so we can
run the same example as above, but include the Basic Authentication needed to authenticate:

.. code-block:: guess

    $ curl http://localhost:5000/flump/user/ -u"test@test.com:password" -i

      HTTP/1.0 200 OK
      Content-Type: application/vnd.api+json
      Content-Length: 237
      Server: Werkzeug/0.11.2 Python/3.4.2
      Date: Fri, 13 Nov 2015 12:55:29 GMT

      {
        "data": [
          {
            "attributes": {
              "email": "test@test.com"
            },
            "id": "1",
            "type": "user"
          }
        ],
        "links": {
          "self": "http://localhost:5000/flump/user/"
        },
        "meta": {
          "total_count": 1
        }
      }

Notice the response body does not include the password of our User (hashed or otherwise)!

We can then run any of the same commands as in the simple Sqlalchemy example above, remembering to include the required username and password in our requests.


Example with limited HTTP Methods
==================================

Before reading through this example, we recommend reading through :ref:`limited-http-methods`.

Now say we only wish to support creating and retrieving entities, we can do this by following the example
shown in `limited-http-methods.py`

As with the examples above, you will first need to change directory to the examples directory

.. code-block:: guess

    $ cd docs/examples

You will then need to install the `basic-requirments.txt` file to run this example:

.. code-block:: guess

    $ pip install -r basic-requirements.txt

You can now run the code from limited-http-methods.py by running:

.. code-block:: guess

    $ python limited-http-methods.py

First off we check we can create a User:

.. code-block:: guess

    $ curl -XPOST http://localhost:5000/flump/user/ -H "Content-Type: application/json" -d '{"data": {"attributes": {"name": "carl"}, "type": "user"}}' -i

    HTTP/1.0 201 CREATED
  Content-Type: application/vnd.api+json
  Content-Length: 169
  Location: https://localhost:5000/flump/user/1
  ETag: "3aed8692-ab10-42f2-ab67-3b24b20b8669"
  Server: Werkzeug/0.11 Python/3.4.2

  {
    "data": {
      "attributes": {
        "name": "carl"
      },
      "id": "1",
      "type": "user"
    },
    "links": {
      "self": "https://localhost:5000/flump/user/1"
    }
  }

We then check we can retrieve the User:

.. code-block:: guess

    curl http://localhost:5000/flump/user/1 -i

    HTTP/1.0 200 OK
    Content-Type: application/vnd.api+json
    Content-Length: 168
    ETag: "3aed8692-ab10-42f2-ab67-3b24b20b8669"
    Server: Werkzeug/0.11 Python/3.4.2

    {
      "data": {
        "attributes": {
          "name": "carl"
        },
        "id": "1",
        "type": "user"
      },
      "links": {
        "self": "http://localhost:5000/flump/user/1"
      }
    }

Which also works! Now let's see what happens when we try to update our User:

.. code-block:: guess

    $ curl -XPATCH http://localhost:5000/flump/user/1 -H "Content-Type: application/json" -d '{"data": {"attributes": {"name": "newcarl"}, "type": "user", "id": "1"}}' -H "If-Match: 3aed8692-ab10-42f2-ab67-3b24b20b8669" -i

    HTTP/1.0 405 METHOD NOT ALLOWED
    Content-Type: application/vnd.api+json
    Content-Length: 68
    Server: Werkzeug/0.11.11 Python/3.5.1
    Date: Wed, 23 Nov 2016 21:44:45 GMT

    {
      "message": "The method is not allowed for the requested URL."
    }

We see that this HTTP method is not implemented. And trying to `DELETE` our User:

.. code-block:: guess

    $ curl -XDELETE http://localhost:5000/flump/user/1 -H "If-Match: 3aed8692-ab10-42f2-ab67-3b24b20b8669" -i

    HTTP/1.0 501 NOT IMPLEMENTED
    Content-Type: application/vnd.api+json
    Content-Length: 83
    Server: Werkzeug/0.11 Python/3.4.2
    Date: Fri, 13 Nov 2015 13:19:34 GMT

    {
      "message": "The server does not support the action requested by the browser."
    }

We see that this is not supported either.

Example with Immutable field
==================================

Before reading through this example, we recommend reading through :ref:`immutable-field`.

Now we address the case where we may have a field which we wish to allow users to create an entity, but not to update it.

As with the examples above, you will first need to change directory to the examples directory

.. code-block:: guess

    $ cd docs/examples

You will then need to install the `basic-requirements.txt` file to run this example:

.. code-block:: guess

    $ pip install -r basic-requirements.txt

You can now run the code from immutable-field.py by running:

.. code-block:: guess

    $ python immutable-field.py


First off we check we can create a User:

.. code-block:: guess

    $ curl -XPOST http://localhost:5000/flump/user/ -H "Content-Type: application/json" -d '{"data": {"attributes": {"name": "carl", "age": 26}, "type": "user"}}' -i

    HTTP/1.0 201 CREATED
    Content-Type: application/vnd.api+json
    Content-Length: 186
    Location: https://localhost:5000/flump/user/1
    ETag: "523624cb-3e0e-457f-9659-334e60dbc72e"
    Server: Werkzeug/0.11 Python/3.4.2

    {
      "data": {
        "attributes": {
          "name": "carl",
          "age": 26
        },
        "id": "1",
        "type": "user"
      },
      "links": {
        "self": "https://localhost:5000/flump/user/1"
      }
    }

Next we try to update the name field, which we have specified as being immutable:

.. code-block:: guess

    $ curl -XPATCH http://localhost:5000/flump/user/1 -H "Content-Type: application/json" -d '{"data": {"attributes": {"name": "newcarl"}, "type": "user", "id": "1"}}' -H "If-Match: 523624cb-3e0e-457f-9659-334e60dbc72e" -i

    HTTP/1.0 422 UNPROCESSABLE ENTITY
    Content-Type: application/vnd.api+json
    Content-Length: 194
    Server: Werkzeug/0.11 Python/3.4.2
    Date: Tue, 17 Nov 2015 17:56:15 GMT

    {
      "errors": {
        "data": {
          "attributes": {
            "name": [
              "Can't update immutable fields."
            ]
          }
        }
      },
      "message": "JSON does not match expected schema"
    }

Which as we can see was not possible due to the field being immutable.
