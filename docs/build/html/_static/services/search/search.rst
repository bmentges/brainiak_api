Search
=======

Given a target textual query expression,
the search service tries to match the textual query expression with the label of the items that belong to the search scope.

For the time being, Brainiak only supports textual searches over instances of a given class in a given graph.

The textual pattern provided by the user is wrapped in a query expression such as "*<pattern>*", that allows the pattern
to match in any position of the searched text.

Two supported parameters are:

**pattern**: textual expression that will be matched or partially-matched against some instances in the search scope.
**graph_uri**: Set the graph URI, defining a subset of classes belonging to the search scope.
**class_uri**: Defines the URI of a given class, whose instances' labels should be searched.


**Basic usage**


.. code-block:: bash

  $ curl -s -X GET 'http://brainiak.semantica.dev.globoi.com/_search&graph_uri=place&class_uri=place:Country&pattern=Bra'

.. program-output:: curl -s -X GET 'http://brainiak.semantica.dev.globoi.com/_search&graph_uri=place&class_uri=place:Country&pattern=Bra'  | python -mjson.tool
  :shell:


Response body parameters
------------------------

Example of response:

