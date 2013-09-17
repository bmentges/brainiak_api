
**class_uri**: Set the class URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME/CLASS_NAME``

**class_prefix**: by default, the class URI is defined by the API's convention (context_uri/class_name).
If the convention doesn't apply, provide class_prefix so the URI will be: class_prefix/class_name.  Example:

.. code-block:: http

  'http://brainiak.semantica.dev.globoi.com/place/City/?class_prefix=http%3A//dbpedia.org/'

If no **class_prefix** had been provided, the class URI above would be resolved as: http://semantica.globo.com/place/City.
As **class_prefix** was defined, the class URI will be: http://dbpedia.org/City.
