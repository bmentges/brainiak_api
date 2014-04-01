Stored Queries
==============

In Brainiak, one can store queries that can not fit a URL description or filter using p/o variables in querystring (see :doc:`/services/instance/list_instance`), giving users flexibility to explore the model with complex relationships, graph traversal, etc.

First, users should register a query to be stored.

Users can register a query by performing a request like:

.. code-block:: bash

  $ curl -s -X PUT 'http://brainiak.semantica.dev.globoi.com/_query/my_query_id' -H "X-Brainiak-Client-Id: my_client_id"

The ``my_query_id`` attribute indicates the query identification to be used when executing it.

The ``X-Brainiak-Client-Id`` header is mandatory for access authentication.
Running a query registered for a specific client id will only work with the same client id.

The request payload for registering a query is a JSON like:

.. code-block:: json

  {
    "sparql_template": "select %(class_uri)s from %(graph_uri)s {%(class_uri)s a owl:Class}",
    "description": "This query is so great, it does everything I need to and it is used in apps such and such"
  }

If the request is successful, a 201 status code is returned.

If there is no client id or the JSON is malformed, a 400 status code is returned.

TODO: Example of 400

Now, we have a stored query.
Where is it?

Retrieving and modifying a stored query
---------------------------------------

We store the query in Brainiak, but users might need to retrieve and/or modify a stored query to conform with their needs.

To see registered queries with my client id:

.. code-block:: bash

  $ curl -s -X GET '/_query' -H "X-Brainiak-Client-Id: my_client_id"

The response for this query has the following format:

.. code-block:: json

  {
    "client_id": "my_client_id",
    "items": [
      {
        "resource_id": "my_query_id",
        "description": "my query description",
        "sparql_template": "select ?class_uri from %(graph_uri)s {?class_uri a owl:Class}"
      }
    ]
  }

The result can be navigated using :doc:`/services/pagination`.

To get a specific query definition, registered with my client id:

.. code-block:: bash

  $ curl -s -X GET '/_query/my_query_id' -H "X-Brainiak-Client-Id: my_client_id"

The response is just a dictionary describing the query as in the list above.

.. code-block:: json

  {
    "resource_id": "my_query_id",
    "description": "my query description",
    "sparql_template": "select ?class_uri from %(graph_uri)s {?class_uri a owl:Class}"
  }

Executing query
---------------

Consider the query described above for gettings classes in a graph.

.. code-block:: sql

  select ?class_uri from %(graph_uri)s {?class_uri a owl:Class}

To execute a query just use the ``_result`` modifier.

.. code-block:: bash

  $ curl -s -X GET '/_query/my_query_id/_result?graph_uri' -H "X-Brainiak-Client-Id: my_client_id"

The response is a JSON with a list of dictionaries with the query result.

.. code-block:: json

  {
    "query": ""
    "items": [
      {"graph_uri", "http://semantica.globo.com/graph1/"},
      {"graph_uri", "http://semantica.globo.com/graph2/"}
    ]
  }

Paging
------

``SPARQL`` uses ``LIMIT``/``OFFSET`` query modifiers for pagination.

In Brainiak, we use ``page`` and ``per_page``.
We strongly recommend that variables in query templates use this name convention.
