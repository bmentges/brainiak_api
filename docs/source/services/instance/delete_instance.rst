Delete a Instance
============

This service deletes a instance, given its context, class name and instance id.

Usage
-----

.. code-block:: http

  DELETE 'http://localhost:5100/place/Country/Brazil'

Optional parameters
-------------------

- graph_uri: Set the graph URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME``
- instance_uri: Set the instance URI, for cases where the URI is not like ``http://semantica.globo.com/CONTEXT_NAME/CLASS_NAME/INSTANCE_ID``

Possible responses
-------------------

Status 204
----------

If the `instance exists`_ and there is no conflict_, the response body is a 204 with no response body.

Status 404
----------

.. _`instance exists`:

If the instance does not exist, the response is a 404 with a JSON
informing the error

.. include :: examples/delete_instance_404.rst

Status 409
----------

.. _conflict:

When there is a conflict, i.e. the instance is refered by another, there is a dependency between them and
therefore, the instance is not deleted, for consistency. To delete an instance you should first delete
instances that depend on it.

The response status is 409 and a JSON informing the dependants is returned.

.. include :: examples/delete_instance_409.rst

Status 400
----------

If there are unknown parameters in the request, the response is a 400
with a JSON informing the wrong parameters and the accepted ones.

.. include :: examples/delete_instance_400.rst
