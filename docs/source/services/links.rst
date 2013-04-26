.. _links_spec:

Links Specification
-------------------

In our API, successful responses have a ``links`` section that state
possible actions for the resource being retrieved.
For more about this concept, see :doc:`../concepts` and :doc:`../concepts/hypermedia`.

For example:

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
        href: "http://api.semantica.dev.globoi.com/person/Gender",
        method: "GET",
        rel: "inCollection"
      },
      {
        "href": "http://api.semantica.dev.globoi.com/person/Gender/Male",
        "method": "PUT",
        "schema": {"$ref": "http://api.semantica.dev.globoi.com/person/Gender/_schema"}
        "rel": "replace"
      },
      {
        "href": "http://api.semantica.dev.globoi.com/person/Gender/Male",
        "method": "DELETE",
        "rel": "delete"
      }
    ]
  }


The URLs in ``href`` can be exact URLs or templates described by `URI template`_.
When they are templates, each placeholder variable of the template should have the respective variable
defined in each entry of the ``items`` section.
For example:

.. highlight:: json

::

  { "items": [
      {
        "title": "Europa",
        "instance_prefix": "http://semantica.globo.com/place/Continent/",
        "@id": "http://semantica.globo.com/place/Continent/Europe",
        "resource_id": "Europe"
      }
    ],
    "links": [
      {
        "href": "http://api.semantica.dev.globoi.com/place/Continent/{resource_id}?instance_prefix={instance_prefix}",
        "method": "GET",
        "rel": "item"
      }
    ]
  }


.. _`URI template`: http://tools.ietf.org/html/rfc6570


Rel Vocabulary
---------------

In the description below we use the term ``target`` to designate the resource retrieved that owns the link relations.
Unless specified otherwise, GET is the default HTTP method used in each of the link relations.

Defined by the ``rel`` key, the possible link relations are:

self
........

The target resource URL itself, i.e. a URL to the target resource that owns the links.


create
..........

Refers to a resource that can be used to create other resources of the same type as the target.


edit
........

Refers to a resource that can be used to edit incrementally the target.

Method: PATCH


replace
...........

Refers to a resource that can be used to edit the target by entirely redefining its content.
When using ``replace``, the target will be removed and inserted again.

Method: PUT

More about the `difference between HTTP PUT and PATCH`_.

.. _`difference between HTTP PUT and PATCH`: http://tools.ietf.org/html/rfc5789


delete
..........

Delete the target.

Method: DELETE


describedBy
...............

Refers to a resource providing information about the target's type in json-schema notation.


inCollection
................

Refers to the list of resources of the same type as the target.


item
........

When the target is a list, the ``item`` refers to each resource within that list.
Moreover, these items are guaranteed *not* to be lists.

instances
.............

When the target is a list, the ``instances`` refers to each resource within that list that represents a sub-list.
Moreover, these resources are guaranteed to be also lists.

first
.........

Refers to the first item of a list.


last
........

Refers to the last item of a list.


next
........

Refers to the next item in a list (e.g. the next page)

previous
............

Refers to the previous item in a list (e.g. the previous page)


Ontology relations links
----------------------------

A flexible relation type is related to the structure of the underlying ontology.
For example, when retrieving a schema for a class, we show specific relations
regarding object properties for that class.

This is useful to a resource that retrives possible values for that predicate
in a class. For example, in a ``links`` section in a schema for Person:

.. highlight:: json

::

  {
    "href": "http://api.semantica.dev.globoi.com/place/Country",
    "rel": "upper:nationality"
  }

This link states that Person has an attribute ``upper:nationality``
and the possible values can be retrieved by using the resource
in ``http://api.semantica.dev.globoi.com/place/Country``, which returns a
list of instances of countries. In this case, the country
represents the nationality of a Person.
