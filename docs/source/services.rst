Services
=============

The API services should be easy to remember, easy to use, and extensible.

We follow the principles of `REST <http://en.wikipedia.org/wiki/Representational_state_transfer>`_
and `HATEOAS <http://en.wikipedia.org/wiki/HATEOAS>`_.

For the meaning and rationale of these concepts in our API,
see :ref:`concept-context`, :ref:`concept-schema`, :ref:`concept-collection`, and :ref:`concept-instance`.

**API Services**

.. toctree::
   :maxdepth: 3

   services/domain/domain.rst
   services/context/context.rst
   services/schema/schema.rst
   services/instance/instance.rst
   services/parameters.rst
   services/links.rst
   services/pagination.rst
   services/errors.rst


.. _resource_url_convention:

Convention for URL Resources
----------------------------

We use the following convention for resources:

+---------------------------------------------------------+-----------------------------------------------------------------------+
| http://<domain>/<context_id>                            | Some context                                                          |
+---------------------------------------------------------+-----------------------------------------------------------------------+
| http://<domain>/<context_id>/<schema_id>                | A collection of instances having the same schema in the same context  |
+---------------------------------------------------------+-----------------------------------------------------------------------+
| http://<domain>/<context_id>/<schema_id>/_schema        | The definition of a schema given by schema_id                         |
|                                                         | in the context given by context_id                                    |
+---------------------------------------------------------+-----------------------------------------------------------------------+
| http://<domain>/<context_id>/<schema_id>/<instance_id>  | A instance identified by instance_id having the schema given by       |
|                                                         | schema_id and belonging to the context given by context_id            |
+---------------------------------------------------------+-----------------------------------------------------------------------+

For each resource there is an URI associated with it, by default we adopt the following rules:

============  ===================================================
 Resources               URI
============  ===================================================
 context       <URI_PREFIX><context_id>/
 schema        <URI_PREFIX><context_id>/<schema_id>
 instance      <URI_PREFIX><context_id>/<schema_id>/<instance_id>
============  ===================================================

URI_PREFIX is a global Brainiak configuration option, and inside Globo.com we define it with ``http://semantica.globo.com/``.
These conventions can be overriden by optional parameters described in :ref:`parametrization`.

Service Examples
----------------

**List all contexts**


.. code-block:: http

    GET 'http://localhost:5100'

**List all collections of a context**

.. code-block:: http

  GET 'http://localhost:5100/place'

**List all instances of a collection**

.. code-block:: http

  GET 'http://localhost:5100/place/Country'

**Get a schema of a collection**

.. code-block:: http

  GET 'http://localhost:5100/place/Country/_schema'

Try it yourself: `Schema for Country`_

.. _Schema for Country: http://api.semantica.dev.globoi.com/v2/place/Country/_schema

**Get a instance of a collection**

.. code-block:: http

  GET 'http://localhost:5100/place/Country/Brazil'

Try it yourself: `Brazil (Country Instance)`_

.. _Brazil (Country Instance): http://api.semantica.dev.globoi.com/v2/place/Country/Brazil
