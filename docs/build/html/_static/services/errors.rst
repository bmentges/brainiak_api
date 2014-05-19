Handling Errors
===============

The Brainiak API returns two levels of error information:

 - HTTP error codes and messages in the header

 - A JSON object in the response body with additional details that can help you determine how to handle the error.

The rest of this page provides a reference of Brainiak errors, with some guidance on how to handle them in your app.


Client-side Errors
------------------

There are some possible types of client errors on API calls that receive request bodies, the most common are:

Sending the unknown parameters in the request, the response is a 400 with a JSON informing the wrong parameters and the accepted ones.

.. code-block:: bash

 HTTP/1.1 400 Bad Request

.. program-output:: curl -s 'http://brainiak.semantica.dev.globoi.com/place/Country/Brazil?invalid_param=1' | python -mjson.tool
  :shell:


If the instance does not exist, the response is a 404 with a JSON informing the error

.. code-block:: bash

  HTTP/1.1 404 Not Found
  Content-Length → 73

.. include :: instance/examples/list_instance_404.rst


When there is a conflict, i.e. the instance is refered by another, there is a dependency between them and therefore, the instance cannot be deleted, for consistency. To delete an instance you should first delete instances that depend on it.

.. code-block:: bash

  HTTP/1.1 409 Not  Conflict
  Content-Length → 30

.. include :: instance/examples/delete_instance_409.rst

All error objects have resource and field properties so that your client can tell what the problem is. There’s also an error code to let you know what is wrong with the field. These are the possible validation error codes:


Server-side Errors
------------------

TODO
