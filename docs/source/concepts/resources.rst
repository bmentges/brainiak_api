Ubiquitous Language
===================

Here we explain the main concepts of the API, i.e. this is
our `ubiquitous language <http://martinfowler.com/bliki/UbiquitousLanguage.html>`_.


.. _concept-context:


Context
-------

``Context`` is an isolated data space, defined by some unique ``context_id``.
This ``context_id`` will be used as a namespace.
Each context can hold classes and instance definitions.
A context can be used to represent, for example, some product or some app being developed.

Inside the triplestore, the context is materialized as `a graph`_.
This graph is represented internally by an `URI`_.
This URI is composed by adding a configurable (server-wide) URI_PREFIX to the ``context_id``
For example, inside Globo.com, the Brainiak server is configured with URI_PREFIX="http://semantica.globo.com/".
Thus, the graph URI implicitly associated with context "app1" would be: "http://semantica.globo.com/app1/".
The default prefix can be overridden if necessary using the parameter ``graph_uri``, see more details in :ref:`parametrization`.

.. _a graph: http://www.w3.org/TR/rdf-sparql-query/#GraphPattern
.. _URI: http://www.ietf.org/rfc/rfc3986.txt



.. _concept-schema:

Class
------

Usually database models work with a clear distinction between instances (data) and classes (metadata).
We also make this distinction on the API interface.

A *Class* is a priviledged instance that defines the structure of the data (non-class instances) being stored.
To avoid confusion, we avoid referring to classes calling them *instances*, a term we reserve for *non-class* instances.
Although we prefer ``class``, sometimes we use the term ``schema`` as a synonym.
``Class`` is preferable to ``schema`` in order to avoid the confusion with the listings schemas rendered in json-schema format.

Classes are defined in the RDF/OWL Model, given its high expressivity and flexibility.
Therefore, it will be possible to represent classes in different database models or even translations between them in a common language.

Likewise, we expect a class to be easily written, by using the `Turtle <http://en.wikipedia.org/wiki/Turtle_(syntax)>`_
format, the most compact serialization for ontologies developed in the RDF/OWL model.

.. code-block:: n3

    :City a owl:Class ;
          rdfs:subClassOf :Place .

The class is associated with a ``class_id`` that is unique in the particular ``context`` where it was declared.
Therefore, the class definition belongs to a graph in the triplestore, where it is identified by an URI.
By convention, the class URI is composed by the context's graph URI and the class_id.
For example, consider the class for ``Person`` declared in the context ``person`` whose graph_uri is ``http://semantica.globo.com/person``.
The default URI for this class would be generated as ``http://semantica.globo.com/person/Person``.
The class' URI can be overriden if necessary using the parameter ``class_uri``, see more details in :ref:`parametrization`.

.. _concept-collection:

Collection
----------

We need to distinguish the structure of an instance (class) from a group of instances with the same structure (collection).
Therefore, for each class corresponds a unique collection adn vice-versa.
The collection name and the class name are the same.


.. _concept-instance:

Instance
--------

An instance is a set of data that is treated as a unit, whose structure is described by a class.
The group of instances that share the same class form a collection.
A collection subset or the whole collection is stored in a context.

Instances must be easily retrieved.
Morevoer, "instance queries" must be really simple for developers to understand as they will do way more requests on instances than on classes.
As such, the interface for manipulating instances accepts JSON content_type as most of the RESTful APIs do.



