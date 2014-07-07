Patch an Instance
==================

Edit a part of an existing instance, providing:

- context (graph)
- class (schema)
- instance identifier (id or uri)
- patch body or payload (JSON)

The body must be a **list** and respect RFC-6902: http://tools.ietf.org/html/rfc6902.

Currently the following operations are supported:

1. **replace**: change a property value
2. **add**: add a new property and its value
3. **remove**: remove some existing property (and therefore its value)

**Basic usage**

Consider you have an existing instance:

.. code-block:: bash

  $ curl -s http://brainiak.semantica.dev.globoi.com/place/City/globoland

.. program-output:: curl -s -X PUT -T "services/instance/examples/new_city.json" http://brainiak.semantica.dev.globoi.com/place/City/globoland; curl -s http://brainiak.semantica.dev.globoi.com/place/City/globoland | python -m json.tool
  :shell:

Note that prefixes, such as "upper", are defined in the "@context" section:
`Default prefixes  <http://brainiak.semantica.dev.globoi.com/_prefixes>`_ are implicit and don't need to be declared.

**Replace**

To patch this instance **replacing** some existing property's value, do:

.. code-block:: bash

  $ curl -i -s -X PATCH -d '[{"op": "replace", "path": "upper:name", "value": "New Globoland name"}]' http://brainiak.semantica.dev.globoi.com/place/City/globoland

.. program-output:: curl -i -s -X PATCH -d '[{"op": "replace", "path": "upper:name", "value": "República Federativa do Brasil"}]' http://brainiak.semantica.dev.globoi.com/place/City/globoland
  :shell:


**Remove**

To patch this instance **removing** some property (and its existing values), do:

.. code-block:: bash

  $ curl -i -s -X PATCH -d '[{"op": "remove", "path": "place:latitude"}]' http://brainiak.semantica.dev.globoi.com/place/City/globoland


**Add**

To patch this instance **adding** some property and value, do:

.. code-block:: bash

  $ curl -i -s -X PATCH -d '[{"op": "add", "path": "place:latitude", "value": 11.785}]' http://brainiak.semantica.dev.globoi.com/place/City/globoland


..

Optional query string parameters
--------------------------------

.. include :: ../params/graph_uri.rst
.. include :: ../params/class.rst

**instance_id**: Unique word identifier for an instance. This is composed with ``instance_prefix`` to form an equivalent of ``instance_uri``.

**instance_uri**: Set the instance URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME/CLASS_NAME/INSTANCE_ID``


Possible responses
------------------

**Status 200**

The instance was patched successfully, the response body is empty.

**Status 400**

If there are unknown parameters in the request, the response status code
is 400 and the body contains a JSON containing valid and invalid parameters.

The 400 status may also happen when the JSON provided is invalid:

  $ curl -i -s  -X PATCH -d '[{"op": "replace", "path": "inexistent:property", "value": 123}]' http://brainiak.semantica.dev.globoi.com/place/City/globoland

.. program-output:: curl -i -s  -X PATCH -d '[{"op": "replace", "path": "inexistent:property", "value": "República Federativa do Brasil"}]' http://brainiak.semantica.dev.globoi.com/place/City/globoland
  :shell:

**Status 404**

If the instance does not exist, the response status code is 404.

  $ curl -i -s  -X PATCH -d '[{"op": "replace", "path": "upper:name", "value": "Some new name"}]' http://brainiak.semantica.dev.globoi.com/place/City/InexistentCity

.. program-output:: curl -i -s -X PATCH -d '[{"op": "replace", "path": "upper:name", "value": "República Federativa do Brasil"}]' http://brainiak.semantica.dev.globoi.com/place/City/InexistentCity
  :shell:

**Status 500**

Internal server error. Please, contact the team <semantica@corp.globo.com>
and provide the URL, JSON and error message.
