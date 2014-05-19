Delete a Instance
=================

This service deletes a instance, given its context, class name and instance id.

**Basic usage**

.. code-block:: http

  DELETE 'http://brainiak.semantica.dev.globoi.com/place/Country/Brazil'

Optional parameters
-------------------

.. include :: ../params/graph_uri.rst
.. include :: ../params/class.rst
.. include :: ../params/instance.rst


Possible responses
-------------------

**Status 204**

If the `instance exists`_ and there is no conflict_, the response body is a 204 with no response body.

**Status 400**

If there are unknown parameters in the request, the response is a 400
with a JSON informing the wrong parameters and the accepted ones.

.. include :: examples/delete_instance_400.rst

**Status 404**

.. _`instance exists`:

If the instance does not exist, the response is a 404 with a JSON
informing the error

.. include :: examples/delete_instance_404.rst

**Status 409**

.. _conflict:

When there is a conflict, i.e. the instance is refered by another, there is a dependency between them and
therefore, the instance cannot be deleted, for consistency. To delete an instance you should first delete
instances that depend on it.

The response status is 409 and a JSON informing the dependants is returned.

.. include :: examples/delete_instance_409.rst
