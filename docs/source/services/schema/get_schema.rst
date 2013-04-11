Get a Schema
============

A schema is where the definition of the data structure resides.

In this service, we can get a specific schema of a class in some context.

**Basic usage**


.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/v2/place/City/_schema'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/v2/place/City/_schema' | python -mjson.tool
  :shell:

Why _schema? In our data model we have a clear distinction between class schemas
(structure of instances) and data (instances), and by using a request like
GET <context>/<class> we could not have a clear distinction whether we want
the whole collection of instances of this specific class or we want the schema of this class.

Thus, the _schema suffix is used to distinguish these two use cases.

Optional parameters
-------------------

**lang**: Specify language of labels. Options: pt, en, undefined (do not filter labels)

**graph_uri**: Set the graph URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME``


Possible responses
------------------


**Status 200**


If the class exists, the response body is a JSON representing the class schema.

.. include :: examples/get_schema_200.rst

**Status 400**


If there are unknown parameters in the request, the response is a 400
with a JSON informing the wrong parameters and the accepted ones.

.. include :: examples/get_schema_400.rst

**Status 404**

If the class does not exist, the response is a 404 with a JSON
informing the error

.. include :: examples/get_schema_404.rst
