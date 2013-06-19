Modeling and Ontology Engineering
=================================

The Brainiak API impose on its client applications some ontology modeling restricitons.
In this section we discuss the rationale, limits and benefits related to those decisions.


The need for rdfs:label
-----------------------

We use rdfs:label or any of its derived property as an ubiquitous property, that we can rely on for indexing purposes.
Brainiak uses that property in several queries over the triplestore, and if an instance does not have thsi property defined it may not appear in the results.


Restrictions on subproperties
-----------------------------

While presenting a class definition, all its direct properties are rendered.
Even the properties inherited from ancestor classes are rendered.
However, if a direct property is derived from another property declared in an ancestor class, only the most specific property will be rendered in the class definition.
This is done to avoid duplicated properties in a class definiton.

Moreover, if class ``X`` has two properties ``i`` and ``j`` where ``j`` is a subproperty of ``i``, only ``j`` will show up in the class ``X`` definiton.
So, if the original intention was to show ``i`` and ``j`` as direct properties in class ``X``, then both should be sub-properties of a more generic property in some ancestor class.

