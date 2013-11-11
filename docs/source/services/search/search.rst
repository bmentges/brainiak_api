Search
=======

Given a target textual query expression,
the search service tries to match the textual query expression with the label of the items that belong to the search scope.

For the time being, Brainiak only supports textual searches over instances of a given class in a given graph,
therefore both class and graph must be specified.

The textual pattern provided by the user is internally wrapped in a query expression such as "*<pattern>*", that allows the pattern
to match in any position of the searched text.
For example, the search for ``bla`` is expanded to ``*bla*``.

The mandatory parameters are:

**pattern**: textual expression that will be matched or partially-matched against some instances in the search scope.
**graph_uri**: Set the graph URI, defining a subset of classes belonging to the search scope.
**class_uri**: Defines the URI of a given class, whose instances' labels should be searched.


**Basic usage**


.. code-block:: bash

  $ curl -s -X GET 'http://brainiak.semantica.dev.globoi.com/_search?graph_uri=place&class_uri=place:Country&pattern=Bra'

.. program-output:: curl -s -X GET 'http://brainiak.semantica.dev.globoi.com/_search?graph_uri=place&class_uri=place:Country&pattern=Bra'  | python -mjson.tool
  :shell:


Possible responses
------------------

**Status 200**

If the search is successfull, a response JSON is returned, showing the matched instances.

.. code-block:: bash

  $ curl -s -XPOST 'http://brainiak.semantica.dev.globoi.com/_search?graph_uri=place&class_uri=place:Country&pattern=Bra'

.. include :: examples/search_response.rst

**Status 400**

If the request is malformed due to with invalid parameters, a 400 HTTP error is returned.

This is due to the following reasons:

* Missing required parameters. If the request body does not have the keys ``predicate`` or ``pattern``.

.. include :: examples/suggest_400_missing_parameter.rst

* Unknown predicate. If a predicate is not found in the ontology or does not have a declared ``rdfs:range``.

.. include :: examples/suggest_400_unknown_predicate.rst

* Classes not in range. If the ``search_classes`` parameter has any class that is not in the range of ``predicate``.

For example, if we pass in the request body ``"predicate": "place:partOfContinent"`` and ``"search_classes": ["place:City"]``.

.. include :: examples/suggest_400_classes_not_in_range.rst

* Graphs not in range. If the ``search_graphs`` parameter has any graphs that classes in the range of ``predicate`` are not in.

For example, if we pass in the request body ``"predicate": "place:partOfCity"`` and ``"search_graphs": ["http://semantica.globo.com/person/"]``.

.. include :: examples/suggest_400_graphs_not_in_range.rst

* Graphs without instances. If the predicate's ranges are only classes in graphs without instances, such as ``http://semantica.globo.com/upper/``.

For example, if we pass in the request body ``"predicate": "upper:isPartOf"`` and restrict graphs to ``"search_graphs": ["http://semantica.globo.com/upper/"]``.

.. include :: examples/suggest_400_graphs_without_instances.rst

**Status 404**

If there are no matches in the search engine, a 404 HTTP error is returned.

.. include :: examples/suggest_404.rst

**Status 500**

Internal server error. Please, contact the team <semantica@corp.globo.com>
and provide the URL, JSON and error message.
