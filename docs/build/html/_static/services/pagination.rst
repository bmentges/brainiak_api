Pagination
==========

Requests that return multiple items will be paginated to 20 items by default.
You can specify further pages with the ``?page`` parameter.
For some resources, you can also set a custom page size up to 100 with the ``?per_page`` parameter.
Note that for technical reasons not all endpoints respect the ``?per_page`` parameter, see events for example.


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

