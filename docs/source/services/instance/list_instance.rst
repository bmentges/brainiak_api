List of Instances
=================

This service retrieves all instances of a specific class or Instances
according a propert/value filter. The results are paginated.

**Basic usage**

.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/person/Gender/'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/person/Gender/' | python -mjson.tool
  :shell:

This will retrieve all instances of ``Gender`` in the graph ``person``


Optional parameters
-------------------

.. include :: ../params/lang.rst
.. include :: ../params/pages.rst
.. include :: ../params/graph_uri.rst
.. include :: ../params/class.rst
.. include :: ../params/po.rst

**sort_by**: Defines predicate used to order instances. The sorting can also behave as a **p** filter, read **sort_include_empty**. Usage: ``sort_by=rdfs:label`` or ``sort_by=dbprop:stadium``.

**sort_order**: Defines if ordering will be ascending or descending. The default is ascending. E.g: ``sort_order=asc`` or ``sort_order=desc``.

**sort_include_empty**: By default, items that don't define **sort_by** property are also listed (``sort_include_empty=1``). If it is desired to exclude such items, set ``sort_include_empty=0``.


Possible responses
-------------------


**Status 200**

If there are instances that match the query, the response body is a JSON containing instances' titles, resources_id and @ids (URIs).
By default, the first page containing 10 items is returned (``?page=1&per_page=10``).

.. include :: examples/list_instance_200.rst

**Status 400**

If there are unknown parameters in the request query string, the response status code is 400.
A JSON containing both the wrong parameters and the accepted ones is returned.

.. include :: examples/list_instance_400.rst

**Status 404**

If there are no instances, the response status code is a 404.

.. include :: examples/list_instance_404.rst

**Status 500**

If there was some internal problem, the response status code is a 500.
Please, contact semantica@corp.globo.com informing the URL and the JSON returned.
