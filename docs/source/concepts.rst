Concepts
========


Here we explain the main concepts of the API, i.e. this is
our `ubiquitous language <http://martinfowler.com/bliki/UbiquitousLanguage.html>`_.

.. _concept_context:

Context
-------

Context is an isolated data space, defined by some unique ``context_id``.
This ``context_id`` will also be used as a namespace.

A context can represent, for example, the product or the app being developed.


.. _concept_schema:

Schema
------

Usually database models work with a clear distinction between instances (data) and schema (metadata).
We also make this distinction on the API interface.

A *Schema* is a priviledged instance that defines the structure of the data (non-schema instances) being stored.
To avoid confusion, we avoid referring to Schemas calling them *instances*, a term we reserve for *non-schema* instances.

Schemas are defined in the RDF/OWL Model, given its high expressivity and flexibility.
Therefore, it will be possible to represent schemas in different database models or even translations between them
in a common language.

Likewise, we expect a schema to be easily written, by using the `Turtle <http://en.wikipedia.org/wiki/Turtle_(syntax)>`_
format, the most compact serialization for ontologies developed in the RDF/OWL model.

.. code-block:: guess

    :City a owl:Class ;
          rdfs:subClassOf :Place .


.. _concept_collection:

Collection
----------

A schema defines a group of instances of the same type.
This group is hereby named a collection.

The collection name is the same as the schema (or class) name.


.. _concept_instance:

Instance
--------

Instances must be easily retrieved and "instance queries" must be really simple
for developers to understand as they will do way more requests on instances than on schemas.
As such, the interface for manipulating instances also accept JSON as content_type as most of the RESTful APIs do.

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
