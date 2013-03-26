Links Specification
===================

In our API, successful responses have a ``links`` section that state
possible actions for the resource being retrieved. For more about this concept, see :doc:`concepts`.

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

The possible link relations are (defined in the ``rel`` key):

**self**

The resource URI itself, i.e. an identifier to the link's context.

Method: GET

**create**

Refers to a resource that can be used to create a resource of the same type
as the link's context.

**edit**

Refers to a resource that can be used to edit the link's context.

Method: PATCH

**replace**

Refers to a resource that can be used to edit the link's context entirely, i.e. the difference
from edit to replace is that the resource will be removed and inserted again.

Method: PUT

More about the `difference between HTTP PUT and PATCH`_.

.. _`difference between HTTP PUT and PATCH`: http://tools.ietf.org/html/rfc5789

**delete**

Delete the current resource.

Method: DELETE

**describedBy**

Refers to a resource providing information about the link's context.

Method: GET

**list**

Refers to the list of resources of the sama type as the link's context.

Method: GET

**item**

Refers to a URI containing a `URI template`_ (e.g. ``http://localhost:5100/person/Person/{resource_id}``) to retrieve a specific item
of a list.

.. _`URI template`: http://tools.ietf.org/html/rfc6570

Method: GET

**first**

Refers to the first item of a list.

Method: GET

**last**

Refers to the last item of a list.

**next**

Refers to the next item in a list (e.g. the next page)

**previous**

Refers to the previous item in a list (e.g. the previous page)

**Ontology relations links**

A flexible relation type is related to the structure of the underlying ontology.
For example, when retrieving a schema for a class, we show specific relations
regarding object properties for that class.

This is useful to a resource that retrives possible values for that predicate
in a class. For example, in a ``links`` section in a schema for Person:

.. highlight:: json

::

  {
    "href": "http://localhost:5100/place/Country",
    "rel": "upper:nationality"
  }

This link states that Person has an attribute ``upper:nationality``
and the possible values can be retrieved by using the resource
in ``http://localhost:5100/place/Country``, which returns a
list of instances of countries. In this case, the country
represents the nationality of a Person.
