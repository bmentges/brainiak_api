API concepts
=============

Here we explain the main concepts of the API, i.e. this is
our `ubiquitous language <http://martinfowler.com/bliki/UbiquitousLanguage.html>`_.

.. _concept_context:

Context
-------

An isolated context of data, defined by some unique slug that defines its namespace.

It might represent, for example, the product or the app being developed.

.. _concept_schema:

Schema
------

Most of database models work with a clear distinction between instances (data) and
schema (metadata), we also make this distinction on the API interface.

Therefore, a *Schema* is a structure that defines the data being stored.

Schemas are defined in the RDF/OWL Model, given its high expressivity and flexibility. Like so,
it will be possible to represent schemas in different database models or even translations between them
in a common language.

Likewise, we expect a schema to be easily written, by using the Turtle format, the
most compact serialization of ontologies developed in the RDF/OWL model.

.. _concept_collection:

Collection
----------

A schema defines a group of instances of the same type.
This group is hereby named a collection.

The collection name is based on the class name plural (e.g. City -> cities)

.. _concept_instance:

Instance
--------

Instances must be easily retrieved and "instance queries" must be really simple
to developers to understand as they will do way more requests on instances than on schemas. As such,
the interface for manipulating instances also accept JSON as content_type as most of the RESTful APIs do.
