.. _edit_instance

Edit a Instance
===============

This service allows the edition of an instance, provided its context, class name, instance identifier and JSON.

**Basic usage**

.. code-block:: bash

  $ curl -i -X PUT -T "edit_female.json" http://api.semantica.dev.globoi.com/v2/person/Gender/Female

.. code-block:: http

    HTTP/1.1 200 OK
    Server: nginx
    Date: Thu, 28 Mar 2013 15:51:59 GMT
    Content-Type: application/json; charset=UTF-8
    Content-Length: 976
    Connection: keep-alive
    Access-Control-Allow-Origin: *

    {"rdfs:label": ["Feminino", "Feminino", "Feminino 2", "Feminino 2"], "rdf:type": ["person:Gender", "person:Gender", "person:Gender", "person:Gender"], "links": [{"href": "http://api.semantica.dev.globoi.com/person/Gender/Female", "rel": "self"}, {"href": "http://api.semantica.dev.globoi.com/person/Gender/_schema", "rel": "describedBy"}, {"href": "http://api.semantica.dev.globoi.com/person/Gender/Female", "method": "DELETE", "rel": "delete"}, {"href": "http://api.semantica.dev.globoi.com/person/Gender/Female", "method": "PUT", "rel": "replace"}], "@context": {"person": "http://semantica.globo.com/person/", "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdfs": "http://www.w3.org/2000/01/rdf-schema#"}, "$schema": "http://api.semantica.dev.globoi.com/person/Gender/_schema", "@id": "http://semantica.globo.com/person/Gender/Female", "@type": "person:Gender"}

Sample JSON "edit_female.json":

.. include :: examples/edit_instance_payload.rst

Note that prefixes are defined in the "@context" section. 
`Default prefixes  <http://api.semantica.dev.globoi.com/v2/prefixes>`_ are implicit and don't need to be declared.

Optional query string parameters
--------------------------------

**class_prefix**: by default, the class URI is defined by the API's convention (context_uri/class_name). If the convention doesn't apply, provide class_prefix so the URI will be: class_prefix/class_name.  Example:

.. code-block:: http

  PUT 'http://localhost:5100/place/City?class_prefix=http%3A//dbpedia.org/' new_city.json

If no **class_prefix** had been provided, the class URI above would be resolved as: http://semantica.globo.com/place/City. As **class_prefix** was defined, the class URI will be: http://dbpedia.org/City.

Possible responses
------------------

**Status 200**

The instance was edited successfully, the response body is the modified instance.

**Status 400**

If there are unknown parameters in the request, the response status code
is 400 and the body contains a JSON containing valid and invalid parameters.

.. include :: examples/get_instance_400.rst

The 400 status may also happen when the JSON provided is invalid:

.. include :: examples/edit_instance_400.rst

**Status 404**

If the class does not exist, the response status code is 404.

.. code-block:: http

  PUT 'http://localhost:5100/place/City/InexistentCity' JSON

.. include :: examples/create_instance_404.rst

**Status 500**

Internal server error. Please, contact the team <semantica@corp.globo.com>
and provide the URL, JSON and error messaage.
