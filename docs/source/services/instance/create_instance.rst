Create a Instance
=================

This service allows the creation of a new instance, provided its context, class name and JSON.

**Basic usage**

.. code-block:: bash

  $ curl -i -X POST -T "new_york_city.json" http://api.semantica.dev.globoi.com/place/City/

.. program-output:: curl -i -s -H "Expect:" -X POST -T "services/instance/examples/new_city.json" http://api.semantica.dev.globoi.com/place/City/
  :shell:

Sample JSON "new_city.json" for the class City_:

.. _City: http://api.semantica.dev.globoi.com/place/City/_schema

.. include :: examples/create_instance_payload.rst

Note that prefixes are defined in the "@context" section.
`Default prefixes  <http://api.semantica.dev.globoi.com/prefixes>`_ are implicit and don't need to be declared.

Besides using ``POST`` to create new instances, it is also possible to use ``PUT`` (for more information, see :ref:`edit_instance`).
In this case, the ``instance_id`` should be provided, which must be unique in the specified context.
The recommended policy is to use ``POST``, as it will assure uniqueness of the identifiers.

..

Optional query string parameters
--------------------------------

**class_prefix**: by default, the class URI is defined by the API's convention (context_uri/class_name). If the convention doesn't apply, provide class_prefix so the URI will be: class_prefix/class_name.  Example:

.. code-block:: http

  POST 'http://api.semantica.dev.globoi.com/place/City/?class_prefix=http%3A//dbpedia.org/' new_city.json

If no **class_prefix** had been provided, the class URI above would be resolved as: http://semantica.globo.com/place/City. As **class_prefix** was defined, the class URI will be: http://dbpedia.org/City.

**graph_uri**: Set the graph URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME``


Possible responses
------------------


**Status 201**

The instance was created successfully, the response body is empty.
The URI of the new instance is identified by the "Location" header in
the HTTP response.

Note that the URI of a instance is not the same as the URL to retrieve
a instance from the API. For retrieving it, use the retrieve instance primitive <>.

**Status 400**

If there are unknown parameters in the request, the response status code
is 400 and the body contains a JSON containing valid and invalid parameters.

.. include :: examples/get_instance_400.rst

The 400 status may also happen when the JSON provided is invalid:

.. include :: examples/create_instance_400.rst

**Status 404**

If the class does not exist, the response status code is 404.

.. code-block:: http

  POST 'http://api.semantica.dev.globoi.com/place/Person/' JSON

.. include :: examples/create_instance_404.rst

**Status 500**

Internal server error. Please, contact the team <semantica@corp.globo.com>
and provide the URL, JSON and error messaage.
