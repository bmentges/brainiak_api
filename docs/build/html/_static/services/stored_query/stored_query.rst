Stored Queries
==============

Users of the Braniak API can define and store queries that do more than retrieve objects (instances or classes) or
apply simple filters using p/o variables in querystring (see :doc:`/services/instance/list_instance`).
Stored queries give users flexibility to explore the model with complex relationships, graph traversal, etc.

Stored queries gives users the flexibility to explore the model with all the power of SPARQL,
including complex relationships and graph traversal.

The first step is to register (store) a query.


Creating or modifying a query definition
----------------------------------------

The service to register a query is the same used to update it.

The ``X-Brainiak-Client-Id`` header is mandatory for access authentication.

The client id used during query registration must be the same used during UPDATE and DELETE.

Users can register a query by performing a request like:

.. code-block:: bash

  $ curl -s -X PUT 'http://brainiak.semantica.dev.globoi.com/_query/my_query_id' -T payload.json -H "X-Brainiak-Client-Id: my_client_id"

The ``my_query_id`` attribute indicates the query identification to be used when executing it.


The payload.json is a JSON object with the query definition and metadata:
The required attributes are: sparql_template and description.


.. code-block:: json

  {
    "sparql_template": "SELECT %(class_uri)s FROM %(graph_uri)s {%(class_uri)s a owl:Class}",
    "description": "This query is so great, it does everything I need  and it is used in apps such and such"
  }

When the request is successful for creating a query, a ``201`` status code is returned.
For modifying existent queries, a ``200`` status code is returned.

Notice that just read-only (e.g. SELECT) queries would be allowed to be registered.
SPARQL 1.1 queries (most specifically, `SPARUL <http://en.wikipedia.org/wiki/SPARUL>`_ ones) such as CONSTRUCT, MODIFY, INSERT, DELETE would be rejected with HTTP status code ``403``.

Malformed queries with invalid JSON or missing required attributes (e.g sparql_template) would be rejected with HTTP status code ``400``.


Listing registered queries
--------------------------

We store the queries in Brainiak, but users might need to retrieve and/or modify a previously stored query.
To list all queries registered, do:


.. To list all queries registered with the same my_client_id, do:

.. code-block:: bash

  $ curl -s -X GET 'http://brainiak.semantica.dev.globoi.com/_query'

.. -H "X-Brainiak-Client-Id: my_client_id"


The response for this query has the following format:

..    "client_id": "my_client_id",

.. code-block:: json

  {
    "items": [
      {
        "resource_id": "my_query_id",
        "description": "my query description",
        "sparql_template": "SELECT ?class_uri FROM %(graph_uri)s {?class_uri a owl:Class}"
      }
    ]
  }

The result can be navigated using :doc:`/services/pagination`.

.. If the given client_id is not found the request is invalid and will be rejected with HTTPstatus code ``404``.


Retrieving a specific query definition
--------------------------------------

To retrieve a specific query definition, registered with my_query_id:

.. code-block:: bash

  $ curl -s -X GET '/_query/my_query_id'

.. -H "X-Brainiak-Client-Id: my_client_id"


The response is the same JSON object that was used to register the query.

.. code-block:: json

  {
    "description": "my query description",
    "sparql_template": "SELECT ?class_uri FROM %(graph_uri)s {?class_uri a owl:Class}"
  }


If my_query_id was not registered previously, the request is invalid and will be rejected with HTTP status code ``404``.


Deleting a query
----------------

To delete a stored query, registered with my_query_id:

.. code-block:: bash

  $ curl -s -X DELETE '/_query/my_query_id' -H "X-Brainiak-Client-Id: my_client_id"

If the query exists and was successfuly deleted, a ``204`` status code is returned.
If the query does not exists and there was an attempt to delete it, a ``404`` status code will be returned.


Executing a query
-----------------

Consider the query described above for gettings classes in a graph.

.. code-block:: sql

  SELECT ?class_uri FROM %(graph_uri)s {?class_uri a owl:Class}

To execute a query just use the ``_result`` modifier.

.. code-block:: bash

  $ curl -s -X GET '/_query/my_query_id/_result?graph_uri=http%3A%2F%2Fsemantica.globo.com%2Fgraph%2F'
.. -H "X-Brainiak-Client-Id: my_client_id"

The response is a JSON with a list of dictionaries, each with all the matched variables in the query.

.. code-block:: json

  {
    "item_count": 2,
    "items": [
      {"class_uri": "http://semantica.globo.com/graph/Class1"},
      {"class_uri": "http://semantica.globo.com/graph/Class2"}
    ]
  }


Counting in queries
+++++++++++++++++++

When using the aggregator COUNT in SPARQL, for instance consider the following query:


.. code-block:: sparql

    SELECT DISTINCT COUNT(?o) {?s a ?o}


This would return a result with ``callret-N`` as variable name:

.. code-block:: json

    {"items": [{"callret-0": "42"}]}


In order to have a more descriptive result, use SPARQL ``AS`` modifier to create an alias.

.. code-block:: sparql

  SELECT DISTINCT COUNT(?o) AS ?count {?s a ?o}


This would return the more descriptive result:

.. code-block:: json

    {"items": [{"count": "42"}]}



Paging
------

SPARQL uses ``LIMIT``/``OFFSET`` query modifiers for pagination.

In Brainiak, we use ``page`` and ``per_page`` as reserved pagination parameters.
We strongly recommend that variables in query templates **DO NOT USE** these reserved names.
