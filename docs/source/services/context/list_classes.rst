List Classes of a Context
=========================

This service retrieves all classes of a specific context (i.e. graph).
The results are paginated.

**Basic usage**

.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/v2/place/'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/v2/place/' | python -mjson.tool
  :shell:

This will retrieve all classes in the ``place`` graph.

Optional parameters
-------------------

**lang**: Specify language of labels. Options: pt, en, undefined (do not filter labels)

**graph_uri**: Set the graph URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME``

**page**: The page you want to retrieve. The default value is ``1``, i.e. the first page

**per_page**: Defines how many items you want to retrieve per page. The default value is ``10``

Possible responses
-------------------

**Status 200**

If there are classes in this graph, the response body is a JSON containing classes' titles and @ids (URIs).
By default, the first page containing 10 items is returned (``?page=1&per_page=10``).

.. include :: examples/list_classes_200.rst

**Status 400**

If there are unknown parameters in the request query string, the response status code is 400.
A JSON containing both the wrong parameters and the accepted ones is returned.

.. include :: examples/list_classes_400.rst

**Status 404**

If there are no instances, the response status code is a 404.

.. include :: examples/list_classes_404.rst

**Status 500**

If there was some internal problem, the response status code is a 500.
Please, contact semantica@corp.globo.com informing the URL and the JSON returned.

