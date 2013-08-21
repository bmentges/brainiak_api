Suggest
=======

The suggest service searchs, for a given object property (a predicate whose value is a object, a URI),
instances that could be added to the predicate value.
The instances must match a pattern passed in request to be retrieved.

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



Optional query string parameters
--------------------------------


