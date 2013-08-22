Suggest
=======

The suggest service searchs, for a given object property (a predicate whose value is a object, a URI),
instances that could be added to the predicate value.

The instances must also match a pattern passed in request to be retrieved.

**Basic usage**


.. code-block:: bash

  $ curl -s -XPOST 'http://api.semantica.dev.globoi.com/_suggest' -T "suggest_search.json"

.. program-output:: curl -s -X POST 'http://api.semantica.dev.globoi.com/_suggest' -T "services/suggest/examples/suggest_minimal_example.json" | python -mjson.tool
  :shell:

A JSON must be passed in the request body. The minimal JSON is shown below:

.. include :: examples/suggest_minimal_example_payload.rst

The ``predicate`` parameter represents the target predicate.
For example, the predicate in the example above is ``place:partOfCity``.
The range (types of possible values) of this predicate is ``place:City``.
Therefore, the ``_suggest`` service will try to match instances of ``place:City``.

The ``pattern`` parameter indicates the search keyword used to match instances.
Usually, the pattern must occur in the label of the instances, but one might want to search in other properties as well,
using the ``search_fields`` optional parameter (see in :ref:`optional_body_parameters`).

.. _optional_body_parameters:

Optional body parameters
------------------------

Some optional parameters can be passed in request body:

.. include :: examples/suggest_full_example_payload.rst

``search_fields`` indicates optional fields to search on. Without this parameter, we match for values in ``rdfs:label`` and its subproperties.

``search_classes`` indicates the classes in which we search instances, thus restricting the result of the predicate range.

If this parameter has classes that are not in the predicate range, a 400 error is returned.

``search_graphs`` indicates the graphs in which we look for instances, thus restricting the result of the graphs in which the classes in the predicate ranges are in.

If this parameter has graphs that the classes in the predicate range are not in, a 400 error is returned.


Optional query string parameters
--------------------------------

.. include :: ../params/item_count.rst
.. include :: ../params/pages.rst


Possible responses
------------------

**Status 200**

If the search is successfull a response JSON is returned, showing the matched instances.

.. code-block:: bash

  $ curl -s -XPOST 'http://api.semantica.dev.globoi.com/_suggest' -T "suggest_search.json"

.. include :: examples/suggest_response.rst

**Status 400**

If the request is malformed, with invalid parameters, a 400 HTTP error is returned.

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
