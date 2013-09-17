Get an Instance
================

This service retrieves all information about a instance, given its context, class name and instance id.

**Basic usage**

.. code-block:: bash

  $ curl -s 'http://brainiak.semantica.dev.globoi.com/person/Gender/Female'


Optional parameters
-------------------

.. include :: ../params/default.rst
.. include :: ../params/graph_uri.rst
.. include :: ../params/instance.rst


Possible responses
-------------------


**Status 200**

If the instance exists, the response body is a JSON with all instance information and links to related actions.

.. program-output:: curl -s 'http://brainiak.semantica.dev.globoi.com/place/Country/Brazil' | python -mjson.tool
  :shell:

**Status 400**

If there are unknown parameters in the request, the response is a 400
with a JSON informing the wrong parameters and the accepted ones.

.. program-output:: curl -s 'http://brainiak.semantica.dev.globoi.com/place/Country/Brazil?invalid_param=1' | python -mjson.tool
  :shell:

**Status 404**

If the instance does not exist, the response is a 404 with a JSON
informing the error

.. include :: examples/get_instance_404.rst
