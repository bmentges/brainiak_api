Handling Errors
===============


Client-side Errors
------------------

There are some possible types of client errors on API calls that receive request bodies, the most common are:

Sending the unknown parameters in the request, the response is a 400 with a JSON informing the wrong parameters and the accepted ones.

.. code-block:: bash

 HTTP/1.1 400 Bad Request

.. include :: services/instance/examples/get_instance_400.rst


If the instance does not exist, the response is a 404 with a JSON informing the error

.. code-block:: bash

  HTTP/1.1 404 Not Found
  Content-Length → 73

.. include :: services/instance/examples/list_instance_404.rst


When there is a conflict, i.e. the instance is refered by another, there is a dependency between them and therefore, the instance cannot be deleted, for consistency. To delete an instance you should first delete instances that depend on it.

.. code-block:: bash

  HTTP/1.1 409 Not  Conflict
  Content-Length → 30

.. include :: services/instance/examples/delete_instance_409.rst

All error objects have resource and field properties so that your client can tell what the problem is. There’s also an error code to let you know what is wrong with the field. These are the possible validation error codes:


Server-side Errors
------------------

TODO
