
**instance_prefix**: by default, the instance URI is defined by the API's convention (context_uri/class_name/instance_name). If the convention doesn't apply, provide instance_prefix so the URI will be: class_instance/instance_name.  Example:

examples:

.. code-block:: http

  'http://brainiak.semantica.dev.globoi.com/place/City/Campinas_SP?instance_prefix=http%3A//dbpedia.org/'

If no **instance_prefix** had been provided, the instance URI above would be resolved as: http://semantica.globo.com/place/City/Campinas_SP. As **instance_prefix** was defined, the instance URI will be: http://dbpedia.org/Campinas_SP.

Other example: Instance URI is http://semantica.globo.com/esportes/atleta/80801

.. code-block:: http

  'http://brainiak.semantica.dev.globoi.com/esportes/Atleta/80801?instance_prefix=http://semantica.globo.com/esportes/atleta/'


example: Instance URI is http://semantica.globo.com/base/Pessoa_ImportacaoEleicoes2012TSE_10000001494 and Graph URI is http://semantica.globo.com/

.. code-block:: http

  'http://brainiak.semantica.dev.globoi.com/base/Pessoa/Pessoa_ImportacaoEleicoes2012TSE_10000001494?instance_prefix=base&graph_uri=glb'

**instance_id**: Unique word identifier for an instance. This is composed with ``instance_prefix`` to form an equivalent of ``instance_uri``.

**instance_uri**: Set the instance URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME/CLASS_NAME/INSTANCE_ID``
