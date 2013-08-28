Releases
========

Version 2.2.0 - 2013/08/29
--------------------------

New features
____________
 - Suggest resource (_suggest) with pagination (uses ElasticSearch)
 - Support to multiple triplestore endpoints

Refactor
________
 - Add @id to context and collection
 - Rename hosts barramento.baas -> barramento.backstage
 - Refactor error messages to adhere to CPM2
 - PUT and POST <instance> response do not have body anymore
 - Removed transactional behavior of POST <instance> regarding ActiveMQ
 - Fix inconsistent resource_id in <instance> JSON Schema
 - Refactor rel=self to always represent base_url for other relative links
 - Root/json_schema is now cached

Fixes
_____
 - Fix at GET <instance>: instance_prefix == null
 - Fix at PUT <instance> expansion URI not being applied to string literals
 - Fix double unicode escaping, so we can use JSON Browser
 - Fix collection pagination JSON Schema rels, so they work when filters "p" and "o" are used. For this purpose, collections now have "previous_args", "next_args", "first_args" and "last_args".


Developers' notes
_________________
 - Add automate tests to check compliance to JSON-Schema Version 3
 - query_sparql interface was refactored


Version 2.1.0 - 2013/08/01
--------------------------

New features
____________

 - New parameters for optional URI expansion in responses: exapnd_uri, expand_uri_keys and expand_uri_values.
 - Root schema now have direct hyperlinks to collection and instance.
 - Instances filter with PO ignores literals' type
 - DOCs are now being deployed by default

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
