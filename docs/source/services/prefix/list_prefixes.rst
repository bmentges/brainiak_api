List of Prefixes
================

This service retrieves registered prefixes, used in compact communication with the API.

**Basic usage**

.. code-block:: bash

  $ curl -s 'http://brainiak.semantica.dev.globoi.com/_prefixes'


Optional parameters
-------------------

.. include :: ../params/pages.rst


Possible responses
-------------------

**Status 200**

The response body is a JSON containing the prefixes in a "@context" section
and the root context, which is a context whose name is not in the prefix URI.

.. program-output:: curl -s 'http://brainiak.semantica.dev.globoi.com/_prefixes' | python -mjson.tool
  :shell:

**Status 400**

If there are unknown parameters in the request query string, the response status code is 400.
A JSON containing both the wrong parameters and the accepted ones is returned.

.. program-output:: curl -s 'http://brainiak.semantica.dev.globoi.com/prefixes?invalid_param=1' | python -mjson.tool
  :shell:

**Status 500**

If there was some internal problem, the response status code is a 500.
Please, contact semantica@corp.globo.com informing the URL and the JSON returned.
