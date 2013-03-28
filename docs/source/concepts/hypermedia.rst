Hypermedia Support
==================

All resources may have one or more links properties linking to other resources.
These are meant to provide explicit URLs so that proper API clients don’t need to construct URLs on their own.
It is highly recommended that API clients use these. Doing so will make future upgrades of the API easier for developers.
All URLs are expected to be proper RFC 6570 URI templates.

TODO: improve


**Links in response**


In hypermedia APIs you should be able to navigate through API services from the ``/``.
In each service there is a link to other related resources. For example, if you
query for a specific resource (a entry in a database), in the response you should
get links to actions related to that resource, like editing it, removing it, etc.

Therefore, in the response we have a ``links`` section like this:

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
        "method": "PATCH",
        "rel": "edit"
      },
      {
        "href": "http://localhost:5100/person/Gender/Male",
        "method": "DELETE",
        "rel": "delete"
      }
    ]
  }
