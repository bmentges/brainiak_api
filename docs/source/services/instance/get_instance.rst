Get a Instance
==============

This service retrieves all information about a instance, given its context, class name and instance id.

**Basic usage**

.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/v2/person/Gender/Female'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/v2/person/Gender/Female' | python -mjson.tool
  :shell:

Optional parameters
-------------------

- lang: Specify language of labels. Options: pt, en, undefined (do not filter labels)
- instance_prefix: by default, the instance URI is defined by the API's convention (context_uri/class_name/instance_name). If the convention doesn't apply, provide instance_prefix so the URI will be: class_instance/instance_name.  Example:

.. code-block:: http

  GET 'http://localhost:5100/place/City/Campinas_SP?instance_prefix=http%3A//dbpedia.org/'

If no **instance_prefix** had been provided, the instance URI above would be resolved as: http://semantica.globo.com/place/City/Campinas_SP. As **instance_prefix** was defined, the instance URI will be: http://dbpedia.org/Campinas_SP.


Possible responses
-------------------


**Status 200**

If the instance exists, the response body is a JSON with all instance information and links to related actions.

.. include :: examples/get_instance_200.rst

**Status 400**

If there are unknown parameters in the request, the response is a 400
with a JSON informing the wrong parameters and the accepted ones.

.. include :: examples/get_instance_400.rst

**Status 404**

If the instance does not exist, the response is a 404 with a JSON
informing the error

.. include :: examples/get_instance_404.rst
