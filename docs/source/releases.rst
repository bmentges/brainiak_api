Next Release
============

Version 2.0.0 - 2013-??-??
--------------------------

 - support for multiple predicates in filters
 - compliance with json-schema (moving links from resource to its respective json-schema)
 - resource prefixes renamed to _prefixes
 - resource version renamed to _version
 - internal caching for the root resource with explicit purge support
 - more examples in the documentation were converted from static files into execution scripts expanded before deploy.
 - previous references to schema renamed to  _schema_list if associated with lists. (COmpatible with other uses at Globo.com)
 - in the classes:
     - besides the type, the format field describes the actual type used inside Virtuoso.
     - the field comment was renamed to description to better comply wiht json-schema specification.


Releases
========


Version 1.1.0 - 2013-05-28
--------------------------

 - notification of instance creation ,removal and update to external event bus through stomp protocol. Using package DAD for notifications to MOM bus.
 - class_prefix argument was added to hypernavigational links.
 - more rigorous argument handling in services, invalid parameters make the service fail. On failure, the valid parameters are informed in the error message.
 - The Content-Type header in HTTP responses now includes the URL for the class given in the response payload.
 - BUGFIX: fixed rdfs:label and rdfs:comment in place/Country/Brazil, now using upper:name and upper:description.
 - BUGFIX: the field rdf:type of any instance only contains the direct class of the instance, blank nodes and other intermediate ancestor classes were removed.


Version 1.0.0  - 2013-04-24
---------------------------

 - first release in production
 - features supported:

    - listing of prefixes, contexts, collections and instances
    - retrieval of schemas and instances
    - creation of instances
    - removal of instances
    - update of instances
