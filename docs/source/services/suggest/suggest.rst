Suggest
=======

The suggest service searchs, for a given predicate, instances that could be
added to the predicate value, in the case of object properties.
The instances must have a match to a pattern passed in the request in order to be retrieved.

**Basic usage**


.. code-block:: bash

  $ curl -s -XPOST 'http://api.semantica.dev.globoi.com/_suggest' -T "suggest_search.json"

A JSON must be passed in the request body. The minimal JSON is shown below:

.. include :: examples/suggest_minimal_example_payload.rst

The ``predicate`` paramater indicates the target predicate.
For example, the predicate in the example above is ``place:partOfCity``.
The range (types of possible values) of this predicate is ``place:City``.
Therefore, the ``_suggest`` service will try to match instance of type ``place:City``.

The ``pattern`` paramater indicates the search keyword used to match instances.
Usually, the pattern must occur in the label of the instances, but one might want to search in other properties as well.

..
  aprogram-output:: curl -s 'http://api.semantica.dev.globoi.com/place/City/_class' | python -mjson.tool .
..  :shell: .
