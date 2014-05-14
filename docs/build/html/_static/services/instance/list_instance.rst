List of Instances
=================

This service retrieves all instances of a specific class or Instances
according a propert/value filter. The results are paginated.

**Basic usage**

.. code-block:: bash

  $ curl -s 'http://brainiak.semantica.dev.globoi.com/place/Continent'


This will retrieve all instances of ``Continent`` in the graph ``place``


Optional parameters
-------------------

.. include :: ../params/default.rst
.. include :: ../params/pages.rst
.. include :: ../params/item_count.rst
.. include :: ../params/graph_uri.rst
.. include :: ../params/class.rst
.. include :: ../params/po.rst
.. include :: ../params/sort.rst
.. include :: ../params/direct_instances_only.rst


Possible responses
-------------------


**Status 200**

If there are instances that match the query, the response body is a JSON containing instances' titles, resources_id and @ids (URIs).
By default, the first page containing 10 items is returned (``?page=1&per_page=10``).

.. program-output:: curl -s 'http://brainiak.semantica.dev.globoi.com/place/Continent?page=1&per_page=10' | python -mjson.tool
  :shell:

If there are no instances for this class, the response will contain a warning and a items list empty.

.. include :: examples/list_instance_no_results.rst

**Status 400**

If there are unknown parameters in the request query string, the response status code is 400.
A JSON containing both the wrong parameters and the accepted ones is returned.

.. program-output:: curl -s 'http://brainiak.semantica.dev.globoi.com/place/Continent?invalid_param=1' | python -mjson.tool
  :shell:

**Status 404**

If the class does not exist, the response status code is a 404.

.. include :: examples/list_instance_404.rst

**Status 500**

If there was some internal problem, the response status code is a 500.
Please, contact semantica@corp.globo.com informing the URL and the JSON returned.
