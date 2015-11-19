=================
Design Decisions
=================

------------------
Minimalism
------------------

By design the `FlumpView` class does not provide many common REST API features, instead it provides easy ways to extend your application for many common use cases.

Pagination
  To implement pagination see the documentation for :ref:`pagesizepagination`.

Authentication
  Implementation is left to the developer, for an example of Basic Auth see :ref:`basic-auth-example`.

.. _etags-design:

-----------------
Etags
-----------------

Every entity used with Flump must have an `etag` field which is used for concurrency control. Any time an entity is updated it must be assigned a new `etag`. This is to ensure users of your API are updating/deleting the current version of the entity.

The current `etag` of the entity will be provided as a response `Etag` header to `GET` and `POST` requests.

In order to update or delete an entity, you must provide the current `Etag` in the `If-Match` request header.

.. _ids-design:

-----------------
Entity ID's
-----------------

All entities used with Flump should be automatically assigned an ID on creation. This is to ensure we have a unique identifier for the entity which can be used when generating URL's.
