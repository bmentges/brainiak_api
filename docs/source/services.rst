Services
=============

The API services interfaces should be easy to remember,
easy to write requests to, and extensible enough
to add new features without making resource URLs
confusing.

We follow the principles of `REST <http://en.wikipedia.org/wiki/Representational_state_transfer>`_
and `HATEOAS <http://en.wikipedia.org/wiki/HATEOAS>`_.

For the meaning and rationale of these concepts in our API,
see :ref:`concept-context`, :ref:`concept-schema`, :ref:`concept-collection`,
and :ref:`concept-instance`.

**List of API Services**

.. toctree::
   :maxdepth: 3

   services/schema/schema.rst
   services/instance/instance.rst
   services/parameters.rst
   services/links.rst
   services/pagination.rst
   services/errors.rst


Interface examples
------------------

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
