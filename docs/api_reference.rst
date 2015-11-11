.. _api:

*************
API Reference
*************

.. module:: marshmallow

FlumpBlueprint
==================

.. autoclass:: flump.FlumpBlueprint
    :members:


FlumpSchema
==================

.. autoclass:: flump.FlumpSchema
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

FlumpView Abstract Methods
---------------------

These methods *must* be implemented by any implementation of `FlumpView`.

.. automethod:: flump.view.FlumpView.get_entity
.. automethod:: flump.view.FlumpView.delete_entity
.. automethod:: flump.view.FlumpView.get_many_entities
.. automethod:: flump.view.FlumpView.get_total_entities


BaseFlumpView
==================

.. autoclass:: flump.base_view.BaseFlumpView
    :members:

PageSizePagination
==================

.. autoclass:: flump.pagination.PageSizePagination
    :members:


schemas
=====================

.. automethod:: flump.schemas.make_data_schema
.. automethod:: flump.schemas.make_response_schema
.. automethod:: flump.schemas.make_entity_schema



_FlumpMethodView
======================

.. autoclass:: flump.base_view._FlumpMethodView
