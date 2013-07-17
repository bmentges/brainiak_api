Future Releases
===============

Version 2.1.0 - 2013/07/18
--------------------------

New features
____________

 - Support to multiple triplestore endpoints


Releases
========

Version 2.0.0 - 2013/07/18
--------------------------

New features
____________

 - Instances list (filtering) resource supports multiple predicates and objects
 - Root resource (/) is currently cached
 - New "purge" HTTP method (both recursive and non-recursive),
   available on cached resources
 - Improve compliance towards json-schema
   ("links" section was moved from the instances to their json-schemas)

Refactor
________

 - Instances list (filtering) resource now applies lang to objects (?o) when 
   literals are provided

 - Resources URLs renamed

   * <resource>/_schema -> <resource>/_schema_list, when related to a list resource
   * /prefixes -> /_prefixes
   * /version -> /_version
   * /status/<dependency> -> /_status/<dependency>

 - Hypermedia links renamed

   * instances -> list
   * create -> add

 - Properties on resources' responses

   * list resources

     + "item_count" property was removed by default
       (do_item_count querystring param should be used to show "item_count")

   * schema resource

     + "format" field, related to "type" field, now uses the same format of the property on the triplestore
     + "comment" -> "description" to better comply with json-schema specification
     + "required" now maps boolean values, instead of an array of strings
     + "_class_prefix" was added to fix navigation of legacy instances
     + content-type "profile" variable scapes querystrings' urls, to please JsonBrowser

Documentation
_____________

 - New hypermedia map

Developers' notes
_________________

 - SPARQL queries logging is now compatible to Globo.com DBA team's expectations
 - Syslog handler now uses LOG_LOCAL3 (before: LOG_SYSLOG)
 - Redis is an optional dependency for running Brainiak locally (tests, however, require it)
 - Cache implementation uses Redis and is optional to run Brainiak
 - Improved test coverage analysis method
 - Updated to Tornado 3.1

Version 1.1.0 - 2013/05/28
--------------------------

 - notification of instance creation, removal and update to external event bus through stomp protocol. Using package DAD for notifications to MOM bus.
 - class_prefix argument was added to hypernavigational links.
 - more rigorous argument handling in services, invalid parameters make the service fail. On failure, the valid parameters are informed in the error message.
 - The Content-Type header in HTTP responses now includes the URL for the class given in the response payload.
 - BUGFIX: fixed rdfs:label and rdfs:comment in place/Country/Brazil, now using upper:name and upper:description.
 - BUGFIX: the field rdf:type of any instance only contains the direct class of the instance, blank nodes and other intermediate ancestor classes were removed.


Version 1.0.0  - 2013/04/24
---------------------------

 - first release in production
 - features supported:

    - listing of prefixes, contexts, collections and instances
    - retrieval of schemas and instances
    - creation of instances
    - removal of instances
    - update of instances
