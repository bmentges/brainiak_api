Suggest
=======

The suggest service searchs, for a given object property (a predicate whose value is a object, a URI),
instances that could be added to the predicate value.

The instances must also match a pattern passed in request to be retrieved.

**Basic usage**


.. code-block:: bash

  $ curl -s -XPOST 'http://api.semantica.dev.globoi.com/_suggest' -T "suggest_search.json"

A JSON must be passed in the request body. The minimal JSON is shown below:

.. include :: examples/suggest_minimal_example_payload.rst

The ``predicate`` parameter represents the target predicate.
For example, the predicate in the example above is ``place:partOfCity``.
The range (types of possible values) of this predicate is ``place:City``.
Therefore, the ``_suggest`` service will try to match instances of ``place:City``.

The ``pattern`` parameter indicates the search keyword used to match instances.
Usually, the pattern must occur in the label of the instances, but one might want to search in other properties as well,
using the ``search_fields`` optional parameter (see in :ref:`optional_body_parameters`).

..
  aprogram-output:: curl -s 'http://api.semantica.dev.globoi.com/place/City/_class' | python -mjson.tool .
..  :shell: .

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

alalalal
