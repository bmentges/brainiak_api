Search
=======

Given a target textual query expression,
the search service tries to match the textual query expression with the label of the items that belong to the search scope.

For the time being, Brainiak only supports textual searches over instances of a given class in a given graph,
therefore both class and graph must be specified.

The textual pattern provided by the user is tokenized and analyzed against a index that contains all the labels for instances.
For example, the search for ``unido`` matches ``Estados Unidos``, ``Reino Unido``, and so on.
The type of query used is a `Elastic Search match query`_.

.. _Elastic Search match query: http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/query-dsl-match-query.html

The mandatory parameters are:

**pattern**: textual expression that will be matched or partially-matched against some instances in the search scope.

**graph_uri**: Set the graph URI, defining a subset of classes belonging to the search scope.

**class_uri**: Defines the URI of a given class, whose instances' labels should be searched.


**Basic usage**


.. code-block:: bash

  $ curl -s -X GET 'http://brainiak.semantica.dev.globoi.com/_search?graph_uri=glb&class_uri=base:Pais&pattern=unido'

.. program-output:: curl -s -X GET 'http://brainiak.semantica.dev.globoi.com/_search?graph_uri=glb&class_uri=base:Pais&pattern=unido'  | python -mjson.tool
  :shell:


Possible responses
------------------

**Status 200**

If the search is successfull, a response JSON is returned, showing the matched instances. For example, for the pattern ``brasil``.

.. code-block:: bash

  $ curl -s -X GET 'http://brainiak.semantica.dev.globoi.com/_search?graph_uri=glb&class_uri=base:Pais&pattern=brasil'

If there are no matches found, the ``"items"`` dict will be empty.

.. include :: examples/search_response.rst

**Status 400**

If the request is malformed due to with invalid parameters, a 400 HTTP error is returned.

This is due to the following reasons:

* Missing required parameters. If the request body does not have the keys ``pattern``, ``graph_uri`` or ``class_uri``.

.. include :: examples/search_400_missing_parameter.rst

**Status 500**

Internal server error. Please, contact the team <semantica@corp.globo.com>
and provide the URL, JSON and error message.
