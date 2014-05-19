.. _edit_instance:

Edit a Instance
===============

This service allows the edition of an instance, provided its context, class name, instance identifier and JSON.

**Basic usage**

.. code-block:: bash

  $ curl -i -X PUT -T "edit_female.json" http://brainiak.semantica.dev.globoi.com/person/Gender/Female

.. code-block:: http

    HTTP/1.1 200 OK
    Server: nginx
    Date: Thu, 28 Mar 2013 15:51:59 GMT
    Content-Type: application/json; charset=UTF-8
    Content-Length: 976
    Connection: keep-alive
    Access-Control-Allow-Origin: *

    {
        "$schema": "http://brainiak.semantica.dev.globoi.com/person/Gender/_schema",
        "@context": {
            "person": "http://semantica.globo.com/person/",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
        },
        "@id": "http://semantica.globo.com/person/Gender/Female",
        "@type": "person:Gender",
        "links": [
            {
                "href": "http://brainiak.semantica.dev.globoi.com/person/Gender/Female",
                "rel": "self"
            },
            {
                "href": "http://brainiak.semantica.dev.globoi.com/person/Gender/_schema",
                "rel": "describedBy"
            },
            {
                "href": "http://brainiak.semantica.dev.globoi.com/person/Gender/Female",
                "method": "DELETE",
                "rel": "delete"
            },
            {
                "href": "http://brainiak.semantica.dev.globoi.com/person/Gender/Female",
                "method": "PUT",
                "rel": "update"
            }
        ],
        "rdf:type": "person:Gender",
        "upper:name":"Feminino",
    }

.. warning::

   When using curl, the "-T" param will append the filename to the actual URL, if the URL parameter ends with a "/".
   In order to avoid that, either remove the last "/" or use '-d @new_york_city.json' to expand the file contents.


Sample JSON "edit_female.json":

.. include :: examples/edit_instance_payload.rst

Note that prefixes are defined in the "@context" section.
`Default prefixes  <http://brainiak.semantica.dev.globoi.com/_prefixes>`_ are implicit and don't need to be declared.


Optional query string parameters
--------------------------------

.. include :: ../params/graph_uri.rst
.. include :: ../params/class.rst
.. include :: ../params/instance.rst


Possible responses
------------------

**Status 200**

The instance was edited successfully, the response body is the modified instance.

**Status 400**

If there are unknown parameters in the request, the response status code
is 400 and the body contains a JSON containing valid and invalid parameters.

.. program-output:: curl -s 'http://brainiak.semantica.dev.globoi.com/place/Country/Brazil?invalid_param=1' | python -mjson.tool
  :shell:

The 400 status may also happen when the JSON provided is invalid:

.. include :: examples/edit_instance_400.rst

**Status 404**

If the class does not exist, the response status code is 404.

.. code-block:: http


.. program-output:: curl -s -X PUT 'http://brainiak.semantica.dev.globoi.com/place/InexistentClass/InvalidInstance' -d '{}' | python -mjson.tool
  :shell:

**Status 500**

Internal server error. Please, contact the team <semantica@corp.globo.com>
and provide the URL, JSON and error messaage.
