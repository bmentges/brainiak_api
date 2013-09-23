Suggest
=======

Given a target predicate (an object property whose value is an object, i.e. an URI),
the suggest service searches for instances that could be set as the predicate's object.

A JSON must be passed in the request's body.

This JSON may have the sections ``search`` and ``response``:

* ``search``: is **obligatory** and is related to what will be searched
* ``response``: is **optional** and refers to what will be retrieved


Two parameters must be defined in ``search``:

**target**

The ``target`` parameter represents the target predicate.

For example, the target in the example below is ``place:partOfCity``.

The range (types of possible values) of this predicate is ``place:City``.
Therefore, the ``_suggest`` service will only try to match instances of ``place:City`` set as the value of ``place:partOfCity``.

**pattern**

The ``pattern`` parameter indicates the search expression used to match instances.
Usually, the pattern is matched against the property ``rdfs:label`` of the instances,
but one might want to search in other properties.
The  optional parameter ``fields`` serves to include other properties (see in :ref:`optional_body_parameters`).

Here is a minimal example of the request body:

.. include :: examples/suggest_minimal_example_payload.rst

**Basic usage**


.. code-block:: bash

  $ curl -s -XPOST 'http://brainiak.semantica.dev.globoi.com/_suggest' -T "suggest_search.json"

.. program-output:: curl -s -X POST 'http://brainiak.semantica.dev.globoi.com/_suggest' -T "services/suggest/examples/suggest_minimal_example.json" | python -mjson.tool
  :shell:


.. _optional_body_parameters:

Optional request body parameters
--------------------------------

Some optional parameters can be passed in request body:

.. include :: examples/suggest_full_example_payload.rst


Optional search fields
----------------------

``instance_fields`` list of optional fields to search on. Each field must be an URI or a CURIE. Without this parameter, only ``rdfs:label`` and its subproperties are matched.

``classes`` list of classes whose instances will be searched, thus restricting the result of the predicate range. Each class must be an URI or a CURIE. If this parameter has classes that are not in the predicate range, a 400 error is returned.

``graphs`` list of graphs in which we look for instances, thus restricting the result of the graphs. By default the graphs considered in the search are those in which the classes (present in the range of the target property) are declared. Each graph must be an URI or a CURIE. If this parameter has graphs that the classes in the predicate range are not in, a 400 error is returned.


Optional response fields
------------------------

``required_fields`` boolean which indicates that fields which have ``owl:minQualifiedCardinality`` equal or larger than ``1`` should be returned. The default is ``true``.

``meta_fields`` list of meta predicates. These meta predicates must be defined in the ontology and might map the most relevant predicates for disambiguation, for instance. Each meta predicate must be an URI or a CURIE.

``class_fields`` list of class predicates whose values should be retrieved, such as class description (``rdfs:comment``) or other properties. Each class field must be an URI or a CURIE.

``classes`` list of classes towards which the instances will be restricted.  Each class must be an URI or a CURIE.

Optional query string parameters
--------------------------------

.. include :: ../params/item_count.rst
.. include :: ../params/pages.rst
.. include :: ../params/expand.rst


Response body parameters
------------------------

Example of response:

.. include :: examples/suggest_full_example_response.rst

``items`` list of instances (more details on the items on :ref:`item_details`)
``item_count`` integer representing the total number of items
``@context`` JSON containing definitions of prefixes used in CURIEs.

.. _item_details:

Response item details
---------------------

Each item has several parameters:

``@id`` string containing the unique identifier (URI) of a certain instance

``title`` string that represents the instance label (``rdfs:label``)

``@type`` class from which the item was instantiated (``rdfs:type``)

``type_title`` label (``rdfs:label``) associated to the instance's class

``class_fields`` JSON that maps the class predicates declared in the request's ``class_fields`` to their respective values for the instance

``instance_fields`` based on the fields defined in the request payload (``fields``, ``required_fields``, ``meta_fields``), return a list of JSONs composed by:

* ``predicate_id`` string containing a URI or a CURIE of the predicate
* ``predicate_title`` string containing the label (``rdfs:label``) of the predicate
* ``object_id`` string containing a URI or a CURIE of the object mapped by the predicate for the given instance
* ``object_title`` string containing the label (``rdfs:label``) of the object mapped by the predicate for the given instance
* ``required`` boolean that represents if a certain predicate is obligatory for the provided class. In other words, if ``owl:minQualifiedCardinality`` equal or larger than ``1``. It is related to ``required_fields``.


Possible responses
------------------

**Status 200**

If the search is successfull, a response JSON is returned, showing the matched instances.

.. code-block:: bash

  $ curl -s -XPOST 'http://brainiak.semantica.dev.globoi.com/_suggest' -T "suggest_search.json"

.. include :: examples/suggest_response.rst

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
