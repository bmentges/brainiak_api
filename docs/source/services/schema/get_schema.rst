Get a Class
============

A class is where the definition of the data structure resides.

In this service, we can get a class defined in some context.

**Basic usage**


.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/place/City/_class'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/place/City/_class' | python -mjson.tool
  :shell:

Why _class? In our data model we have a clear distinction between class
(structure of data) and instances (the data content itself), and by using a request like
GET <context>/<class> we could not have a clear distinction whether we want
the whole collection of instances or we want the definition of this class.

Thus, the _class suffix is used to distinguish the latter case from the former.

Optional parameters
-------------------

.. include :: ../params/lang.rst
.. include :: ../params/graph_uri.rst


Possible responses
------------------


**Status 200**


If the class exists, the response body is a JSON representing the class definition.

.. code-block:: bash

  $ curl -s 'http://api.semantica.dev.globoi.com/place/Country/_class'

.. program-output:: curl -s 'http://api.semantica.dev.globoi.com/place/Country/_class' | python -mjson.tool
  :shell:


**Status 400**


If there are unknown parameters in the request, the response is a 400
with a JSON informing the wrong parameters and the accepted ones.

.. include :: examples/get_schema_400.rst

**Status 404**

If the class does not exist, the response is a 404 with a JSON
informing the error

.. include :: examples/get_schema_404.rst
