Stored Query
============

Users of the Braniak API can define and store queries that do more than retrieve objects (insatnces or classes) or
apply simple filters to collections of instances (see FILTER P/O).

Stored queries gives users the flexibility to explore the model with all the power of SPARQL,
including complex relationships and graph traversal.

First, users must register (store) a query.


Creating or modifying a query definition
----------------------------------------

The service to register a query is the same used to modify it.
The ``X-Brainiak-Client-Id`` header is mandatory for access authentication.
The client id used during query registration must be the same used during UPDATE and DELETE.

Example of registering a query using the following signature:

.. code-block:: bash

  $ curl -s -X PUT 'http://brainiak.semantica.dev.globoi.com/_query/my_great_query' -H "X-Brainiak-Client-Id: my_client_id" -d payload.josn


The payload.json is a JSON object with the query definition and metadata:

.. code-block:: JSON

  {
    "sparql_template": "select ?some_var where { ?some_var a some_graph:some_class}",
    "description": "This query is so great, it does everything I need to and it is used in apps such and such"
  }

Notice that just read-only (i.e. SELECT) queries would be allowed to be registered.
Sparql queries using CONSTRUCT, MODIFY, INSERT, DELETE would be rejected with http status code 403.

Malformed queries with invalid json or missing required attributes (e.g sparql_template) would be rejected with
http status code 400.


Listing registered queries
--------------------------

We store the query in Brainiak, but users might need to retrieve and/or modify a previously stored query.

To list all queries registered with the same my_client_id, do:

.. code-block:: bash

  $ curl -s -X GET '/_query' -H "X-Brainiak-Client-Id: my_client_id"


Retrieving a query definition
-----------------------------

To retrieve a specific query definition, registered with my_client_id:

.. code-block:: bash

  $ curl -s -X GET '/_query/my_great_query' -H "X-Brainiak-Client-Id: my_client_id"

The response is the same json object that was used during query registration, for example:

.. code-block:: JSON

  {
    "sparql_template": "select ?some_var where { ?some_var a some_graph:some_class}",
    "description": "This query is so great, it does everything I need to and it is used in apps such and such"
  }


If my_great_query was not registered previously, the request is invalid and will be rejected with http status code 404.


Executing query
---------------

To execute a query just use the _result modifier

.. code-block:: bash

  $ curl -s -X GET '/_query/my_great_query' -H "X-Brainiak-Client-Id: my_client_id"



GET /_query/<resource_id>/_result


Paging
------

We strongly recommend that variable query templates for paging use naming convention of other Brainaik primitives (``page``, ``per_page``).


Errors
------

