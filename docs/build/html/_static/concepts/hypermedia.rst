.. _hypermedia:

Hypermedia Support
==================

In the words of Jon Moore, ``HATEOAS`` - Hypermedia as the engine of application state is:

::

    You do stuff by reading pages and then either following links or submitting forms.


Any resource may have one or more properties linking to other resources, represented in the resource's link section.
These links are meant to provide explicit URLs so that proper API clients don’t need to hardcode URLs to API services.

In hypermedia APIs you should be able to navigate through API services from the root ``/``.
It is highly recommended that API clients use these links, because API service URLs may change in production without previous notice to clients.
The links are not embedded in the resource, they are present in the schema that described such resource.
In order to obtain the list of links for a given resource, one should follow the profile URL present in the Content-Type response header.
For example:

::

    $ curl -i http://api.semantica.dev.globoi.com

    HTTP/1.1 200 OK
    Content-Type: application/json; profile=http://api.semantica.dev.globoi.com/_schema_list
    Content-Length: 1007
    ...


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
        "href": "http://api.semantica.dev.globoi.com/person/Gender/Male",
        "rel": "self"
      },
      {

        "href": "http://api.semantica.dev.globoi.com/person/Gender/_schema",
        "rel": "describedBy"
      },
      {
        "href": "http://api.semantica.dev.globoi.com/person/Gender/Male",
        "method": "PUT",
        "rel": "update"
      },
      {
        "href": "http://api.semantica.dev.globoi.com/person/Gender/Male",
        "method": "DELETE",
        "rel": "delete"
      }
    ]
  }

A complete documentation of ``rel`` values is given in the section :ref:`links_spec`.
