List of Collections
===================

This service retrieves all classes of a specific context (i.e. graph).
The results are paginated.

**Basic usage**

.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/place/'

This will retrieve all classes in the ``place`` graph.

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/place/' | python -mjson.tool
  :shell:


Optional parameters
-------------------

.. include :: ../params/default.rst
.. include :: ../params/graph_uri.rst
.. include :: ../params/pages.rst
.. include :: ../params/item_count.rst


Possible responses
-------------------

**Status 200**

If there are classes in this graph, the response body is a JSON containing classes' titles and @ids (URIs).
By default, the first page containing 10 items is returned (``?page=1&per_page=10``).

.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/place/?page=1&per_page=10'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/place/?page=1&per_page=10' | python -mjson.tool
  :shell:


**Status 400**

If there are unknown parameters in the request query string, the response status code is 400.
A JSON containing both the wrong parameters and the accepted ones is returned.

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/place/?invalid_param=1' | python -mjson.tool
  :shell:


**Status 404**

If there are no instances, the response status code is a 404.

.. include :: examples/list_collections_404.rst

**Status 500**

If there was some internal problem, the response status code is a 500.
Please, contact semantica@corp.globo.com informing the URL and the JSON returned.

