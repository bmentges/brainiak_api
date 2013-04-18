.. _hypermedia:

Hypermedia Support
==================

Any resource may have one or more properties linking to other resources, represented in the resource's link section.
These links are meant to provide explicit URLs so that proper API clients don’t need to hardcode URLs to API services.
In hypermedia APIs you should be able to navigate through API services from the ``/``.
It is highly recommended that API clients use these links, because API service URLs may change in production without previous notice to clients.
All URLs are expected to be proper RFC 6570 URI templates.

Each link is described by attributes, typically: rel, href and method.
The ``rel`` attribute describes the purpose of the link.
The ``method`` attribute describes which HTTP verb should be used to follow the ink.
The ``href`` attribute describes the URL of the link.
The href value can be an exact string, or a string template whose variable placeholders are given from the items section.

We give an example of a link section below:

.. highlight:: json

::

  {
    "links": [
      {
        "href": "http://localhost:5100/person/Gender/Male",
        "rel": "self"
      },
      {

        "href": "http://localhost:5100/person/Gender/_schema",
        "rel": "describedBy"
      },
      {
        "href": "http://localhost:5100/person/Gender/Male",
        "method": "PUT",
        "rel": "replace"
      },
      {
        "href": "http://localhost:5100/person/Gender/Male",
        "method": "DELETE",
        "rel": "delete"
      }
    ]
  }

A complete documentation of ``rel`` values is given in the section :ref:`links_spec`.
