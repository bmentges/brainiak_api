.. brainiak documentation master file, created by
   sphinx-quickstart on Thu Feb  7 10:40:27 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to brainiak API documentation!
====================================


Linked data offers a set of best practices for publishing, sharing and linking data and information on the web. It is based on use of http URIs and semantic web standards such as RDF.

For some web developers the need to understand the RDF data model and associated serializations and query language (SPARQL) has proved a barrier to adoption of linked data. This project seeks to develop APIs, data formats and supporting tools to overcome this barrier. Including, but not limited to, accessing linked data via a developer-friendly JSON format.

The Brainiak API provides a configurable way to access RDF data using simple RESTful URLs that are translated into queries to a SPARQL endpoint.


.. toctree::
   :maxdepth: 4

   concepts.rst
   services.rst
   links.rst


Client Errors
=============

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

TODO

HEAD
====

Can be issued against any resource to get just the HTTP header info.

**GET**

Used for retrieving resources.

**POST**

Used for creating resources, or performing custom actions (such as
merging a pull request).

**PATCH**

Used for updating resources with partial JSON data.  For instance, an
Issue resource has <code>title</code> and <code>body</code> attributes.  A PATCH request may
accept one or more of the attributes to update the resource.  PATCH is a
relatively new and uncommon HTTP verb, so resource endpoints also accept
POST requests.

**PUT**

Used for replacing resources or collections. For PUT requests
with no <code>body</code> attribute, be sure to set the <code>Content-Length</code> header to zero.

**DELETE**

Used for deleting resources.


Authentication
==============

TODO

Hypermedia
==========

All resources may have one or more links properties linking to other resources. These are meant to provide explicit URLs so that proper API clients don’t need to construct URLs on their own. It is highly recommended that API clients use these. Doing so will make future upgrades of the API easier for developers. All URLs are expected to be proper RFC 6570 URI templates.

Pagination
==========

Requests that return multiple items will be paginated to 20 items by default. You can specify further pages with the ``?page`` parameter. For some resources, you can also set a custom page size up to 100 with the ``?per_page`` parameter. Note that for technical reasons not all endpoints respect the ``?per_page`` parameter, see events for example.

.. code-block:: bash

  $ curl http://loclahost:5100/base/Acao?page=2&per_page=15

The pagination info is included in the Link Session. It is important to follow these Link header values instead of constructing your own URLs.

.. code-block:: bash

  "links": [{
  "href": "http://10.2.180.27:5100/base/Acao?page=1",
  "method": "GET",
  "rel": "first"
  },
  {
  "href": "http://10.2.180.27:5100/base/Acao?page=64",
  "method": "GET",
  "rel": "last"
  },
  {
  "href": "http://10.2.180.27:5100/base/Acao?page=2",
  "method": "GET",
  "rel": "next"
  }]

The possible ``rel`` values are:

**next**

Shows the URL of the immediate next page of results.

**last**

Shows the URL of the last page of results.

**first**

Shows the URL of the first page of results.

**prev**

Shows the URL of the immediate previous page of results.

