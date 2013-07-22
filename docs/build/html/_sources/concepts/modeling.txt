Modeling and Ontology Engineering
=================================

The Brainiak API impose on its client applications some ontology modeling restricitons.
In this section we discuss the rationale, limits and benefits related to those decisions.


The need for rdfs:label
-----------------------

We use ``rdfs:label`` or any of its derived property as an ubiquitous property, that we can rely on for indexing and for showing in user interfaces.
Brainiak uses that property in several queries over the triplestore, and if an instance does not have this property defined it may not appear in the results produced by Brainiak API.


Restrictions on subproperties
-----------------------------

While presenting a class definition, all its direct properties are rendered.
Even the properties inherited from ancestor classes are rendered.
However, if a direct property is derived from another property declared in an ancestor class, only the most specific property will be rendered in the class definition.
This is done to avoid duplicated properties in a class definiton.

For example, in the example below ``subRegionOf`` is a sub-property of ``isPartOf``, but only ``subRegionOf`` will appear when retrieving the schema for class ``Region``.

.. code-block:: n3

    :subRegionOf a owl:ObjectProperty ;
                rdfs:subPropertyOf other:isPartOf ;
                rdfs:domain :Region .

Moreover, if the class ``Region`` had two properties ``prop1`` and ``prop2`` where ``prop2`` is a subproperty of ``prop1``, only ``prop2`` will show up in the class ``Region`` definiton.

.. code-block:: n3

    :prop1 a owl:ObjectProperty ;
                rdfs:domain :Region .

    :prop2 a owl:ObjectProperty ;
                rdfs:subPropertyOf :prop1 ;
                rdfs:domain :Region .

So, if the original intention was to show ``prop1`` and ``prop2`` as direct properties in class ``Region``, then both should be sub-properties of a more generic property with domain and ranges pointing to some ancestor class of the ones referred by the sub-property.
The example below illustrates that approach.


.. code-block:: n3

    :superprop a owl:ObjectProperty ;
               rdfs:domain :Place .

    :Region a owl:Class ;
            rdfs:subClassOf :Place .

    :prop1 a owl:ObjectProperty ;
           rdfs:subPropertyOf :superprop ;
           rdfs:domain :Region .

    :prop2 a owl:ObjectProperty ;
           rdfs:subPropertyOf :superprop ;
           rdfs:domain :Region .

