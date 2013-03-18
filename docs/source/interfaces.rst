API Interface
=============

The API interfaces should be easy to remember,
easy to write requests to, and extensible enough
to add new features without making resource URLs
confusing.

We follow the principles of `REST <http://en.wikipedia.org/wiki/Representational_state_transfer>`_
and `HATEOAS <http://en.wikipedia.org/wiki/HATEOAS>`_.

In all examples from now on we use a context named *place* and a schema named *City*.
All these examples are based on the DBPedia 3.7 English Ontology.

Therefore, the place context in the example represents all subclasses of DBPedia `Place <http://dbpedia.org/ontology/Place>`_,
*city* represents `City <http://dbpedia.org/ontology/City>`_ and so on.

You can query and learn more about this data model using the `DBPedia SPARQL endpoint <http://dbpedia.org/sparql>`_.

For the meaning and rationale of these concepts in our API,
see :ref:`concept_context`, :ref:`concept_schema`, :ref:`concept_collection`,
and :ref:`concept_instance`.

Interfaces
==========

.. toctree::
   :maxdepth: 3

   interfaces/schema/schema.rst
   interfaces/instance/instance.rst


Interface examples
------------------

List all contexts
--------------------------------

.. code-block:: http

    GET 'http://localhost:5100'

List all schemas of a context
-----------------------------

.. code-block:: http

  GET 'http://localhost:5100/place'

Create schema
-------------

.. code-block:: http

  PUT 'http://localhost:5100/place/City/_schema' -H 'Content-type: text/turtle'

The payload for this request will be something like:

.. code-block:: guess

    :City a              owl:Class ;
          owl:subClassOf dbpedia:Place ;
          rdfs:label     "Cidade"@pt ,
                         "City"@en .

Adding instances
----------------

.. code-block:: http

  POST 'http://localhost:5100/tech/Software' -H 'Content-type: application/json'

.. Example of payload:

.. {
    "rdfs:type": "tech_schemas:Software",
    "tech_schemas:name": "Windows 8",
    "tech_schemas:in_category": "tech:software-categories/OperatingSystem"
.. }
