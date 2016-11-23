.. _api:

*************
API Reference
*************

.. module:: marshmallow

FlumpBlueprint
==================

.. autoclass:: flump.FlumpBlueprint
    :members:

FlumpView
==================

.. autoclass:: flump.view.FlumpView

FlumpView HTTP Methods
------------------

.. automethod:: flump.view.FlumpView.get
.. automethod:: flump.view.FlumpView.get_many
.. automethod:: flump.view.FlumpView.get_single
.. automethod:: flump.view.FlumpView.delete
.. automethod:: flump.view.FlumpView.post
.. automethod:: flump.view.FlumpView.patch

FlumpView Properties
---------------------

.. automethod:: flump.view.FlumpView.data_schema
.. automethod:: flump.view.FlumpView.response_schema


Fetcher
==================

.. autoclass:: flump.fetcher.Fetcher
    :members:

OrmIntegration
==================

.. autoclass:: flump.orm.OrmIntegration
    :members:

.. _pagination:

Pagination
==================

.. autoclass:: flump.pagination.BasePagination
    :members:
.. autoclass:: flump.pagination.PageSizePagination
    :members:

Schemas
=====================

.. automethod:: flump.schemas.make_data_schema
.. automethod:: flump.schemas.make_response_schema
.. automethod:: flump.schemas.make_entity_schema


_FlumpMethodView
======================

.. autoclass:: flump.view._FlumpMethodView

Validators
======================

.. autoclass:: flump.validators.Immutable
