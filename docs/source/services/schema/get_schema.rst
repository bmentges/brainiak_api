Get a Schema
============


A schema is where the definition of the data structure resides.

In this service, we can get a specific schema of a class in some context.

Usage
-----

.. code-block:: http

  GET 'http://localhost:5100/place/City/_schema'

Why _schema? In our data model we have a clear distinction between class schemas
(structure of instances) and data (instances), and by using a request like
GET <context>/<class> we could not have a clear distinction whether we want
the whole collection of instances of this specific class or we want the schema of this class.

Thus, the _schema suffix is used to distinguish these two use cases.

Possible responses
-------------------


Status 200
__________

If the class exists, the response body is a JSON representing the class schema.

.. include :: examples/get_schema_200.rst

Status 404
__________

If the class does not exist, the response is a 404 with a JSON
informing the error

.. include :: examples/get_schema_404.rst

Status 400
__________

If there are unknown parameters in the request, the response is a 400
with a JSON informing the wrong parameters and the accepted ones.

.. include :: examples/get_schema_400.rst
