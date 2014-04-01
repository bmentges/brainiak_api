Stored Query
============

In Brainiak, one can store queries that can not fit a URL description or simple filter (see FILTER P/O), giving users flexibility to explore the model with complex relationships, graph traversal, etc.

First, users should register a query to be stored.

Example of registering a query using the following signature:

.. code-block:: bash

  $ curl -s -X PUT 'http://brainiak.semantica.dev.globoi.com/_query/my_great_query' -H "X-Brainiak-Client-Id: my_client_id"

The ``X-Brainiak-Client-Id`` header is mandatory for access authentication.
Running a query registered for a specific client id will only work with the same client id.

The request payload is a JSON like:

.. code-block:: JSON

  {
    "sparql_template": "select",
    "description": "This query is so great, it does everything I need to and it is used in apps such and such"
  }

TODO: Errors

Now, we have a stored query.
Where is it?

Retrieving and modifying a stored query
---------------------------------------

We store the query in Brainiak, but users might need to retrieve and/or modify a stored query.

To see registered queries with my client id, just:

.. code-block:: bash

  $ curl -s -X GET '/_query' -H "X-Brainiak-Client-Id: my_client_id"

To get a specific query definition, registered with my client id:

.. code-block:: bash

  $ curl -s -X GET '/_query/my_great_query' -H "X-Brainiak-Client-Id: my_client_id"

TODO: Errors


Executing query
---------------

To execute a query just use the _result modifier

.. code-block:: bash

  $ curl -s -X GET '/_query/my_great_query' -H "X-Brainiak-Client-Id: my_client_id"



GET /_query/<resource_id>/_result


Paging
------

We strongly recommend that variable query templates for paging use naming convention of other Brainaik primitives (``page``, ``per_page``).
