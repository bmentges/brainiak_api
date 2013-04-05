List of Contexts
================

This primitive retrieves contexts which define classes and/or instances.
Contexts that contain no data are not listed.

**Basic usage**

.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/v2/'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/v2/' | python -mjson.tool
  :shell:


Optional parameters
-------------------

**page**: The page to be retrieved. The default value is ``1``, i.e. the first page.

**per_page**: Defines how many items are retrieved per page. The default value is ``10``

By default, the first page containing 10 items is returned, and it could also be retrieved by:

.. code-block:: http

  GET 'http://api.semantica.dev.globoi.com/v2/?page=1&per_page=10'

Possible responses
-------------------


**Status 200**

If there are contexts, the response body is a JSON containing contexts' titles, resources_id and @ids (URIs).

.. include :: examples/list_context_200.rst

**Status 400**

If there are unknown parameters in the request query string, the response status code is 400.
A JSON containing both the wrong parameters and the accepted ones is returned.

.. include :: examples/list_context_400.rst

**Status 404**

If there are no contexts, the response status code is a 404.

.. include :: examples/list_context_404.rst

**Status 500**

If there was some internal problem, the response status code is a 500.
Please, contact semantica@corp.globo.com informing the URL and the JSON returned.
