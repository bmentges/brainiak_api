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


TODO: improve

**lang**: Specify language of labels. Options: pt, en, undefined (do not filter labels)

**instance_prefix**: by default, the instance URI is defined by the API's convention (context_uri/class_name/instance_name). If the convention doesn't apply, provide instance_prefix so the URI will be: class_instance/instance_name.  Example:

examples:

.. code-block:: http

  GET 'http://localhost:5100/place/City/Campinas_SP?instance_prefix=http%3A//dbpedia.org/'

If no **instance_prefix** had been provided, the instance URI above would be resolved as: http://semantica.globo.com/place/City/Campinas_SP. As **instance_prefix** was defined, the instance URI will be: http://dbpedia.org/Campinas_SP.

Other example: Instance URI is http://semantica.globo.com/esportes/atleta/80801

.. code-block:: http

  GET 'http://localhost:5100/esportes/Atleta/80801?instance_prefix=http://semantica.globo.com/esportes/atleta/'


**graph_uri**: set the graph URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME``

example: Instance URI is http://semantica.globo.com/base/Pessoa_ImportacaoEleicoes2012TSE_10000001494 and Graph URI is http://semantica.globo.com/

.. code-block:: http

  GET 'http://localhost:5100/base/Pessoa/Pessoa_ImportacaoEleicoes2012TSE_10000001494?instance_prefix=base&graph_uri=glb'


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
