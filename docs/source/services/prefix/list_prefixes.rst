List of Prefixes
================

This service retrieves registered prefixes, used in compact communication with the API.

**Basic usage**

.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/v2/prefixes'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/v2/prefixes' | python -mjson.tool
  :shell:

Possible responses
-------------------

**Status 200**

The response body is a JSON containing the prefixes in a "@context" section
and the root context, which is a context whose name is not in the prefix URI.

.. include :: examples/list_prefixes_200.rst
    
**Status 400**

If there are unknown parameters in the request query string, the response status code is 400.
A JSON containing both the wrong parameters and the accepted ones is returned.

.. include :: examples/list_prefixes_400.rst

**Status 500**

If there was some internal problem, the response status code is a 500.
Please, contact semantica@corp.globo.com informing the URL and the JSON returned.
