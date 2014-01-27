Releases
========

Version XXX - TO BE RELEASED
----------------------------

Fixes
_____


- Fixed type mapping to include ``rdfs:Literal`` to ``string``.


Version 2.4.3 - 2013/01/17
--------------------------

New Features
____________

 - Using cached schema in PUT/POST operations on instances.

Fixes
_____

 - Fixed missing querystring parameters when building schema (``/_schema_list``) URL for a collection of instances.
 - Fixing hit ratio calculation in Redis usage statistics ``_status/cache``


Version 2.4.2 - 2013/01/15
--------------------------

New Features
____________

 - More detailed information for ``/_status/cache``, showing Redis usage statistics

Fixes
_____

 - Root resource was not cached including URL parameters, as a side effect pagination would not work for the root resource.
   Now the root is cached with all the URL parameters that were given.
 - Test suite was cleaned up from tests shadowed by homonymous tests.


Version 2.4.1 - 2013/01/10
--------------------------

New Features
____________

 - Support for caching instances.
 - Any recursive purge will expire all instances in the cache for the time being.
 - Support for purging a specific instance (see :doc:`/services/cache`).


Fixes
_____

 - Removing unused param `purge`.
 - Fixed purging schemas (different GET params cached in different keys).
 - The cache key for any instance follows the pattern  ``_@@_/_@@<instance_uri>##instance``
 - When updating an instance via PUT, the cached version was updated although it lacked the ``meta_properties``.
   Now, when updating the cache, the full properties are updated in the cached instance.
 - Fixed problem in ``/_search`` JSON Schema (see :doc:`/services/search/search`).


Developers notes
________________

 - Acceptance test to validate CMA using splinter.


Version 2.4.0 - 2013/11/28
--------------------------

New Features
____________

 - Add service for full text search of instances (see :doc:`/services/search/search`).
 - Add ``X-Brainiak-Resource-Uri`` to response header when creating instances (URI of instance created)
 - Internationalization of error messages
 - Portuguese version of error messages, despite English (default)
 - Validate value uniqueness when property has the annotation property specified in ``settings.ANNOTATION_PROPERTY_HAS_UNIQUE_VALUE``
 - Validate data when adding or editing instances (uniqueness, type, required). If the data isn't compatible to the schema, the response status code is 400 and the payload contains a list with all the inconsistencies.

Fix
___

 - Bugfix for absent ``Access-Control-Allow-Origin: *`` in error responses
 - When retrieving instances, blank nodes are ignored in the response
 - class_prefix was being rendered with an incorrect trailing ``:``. This char ``:`` is not part of the URL.

Enhancements
____________

 - Use relative URLS in class schema (it was absulte before this release)
 - Add ``rel='create'`` to class schema
 - Add ``rel='suggest'`` to class schema
 - Add ``rel='create'`` to class schema
 - Add ``rel='search'`` to instances' collection
 - Add *temporary*  duplicate ``title`` to collection JSON schema, for compliance with CMAaaS
 - Add ``_type_title`` to each item in Suggest response
 - Add X-Brainiak-Resource-Uri to header, in order to refer to the URI when a instance is created
 - Rename ``rel='instance'`` to ``rel='relatedInstance'`` and change variable template, for compliance with CMAaaS
 - Rename titles in JSON-Schemas for root, context and collection
 - Remove header ``X-Brainiak-Cache-All`` (functionality is available using ``X-Brainiak-Cache-Recursive``)

Developers notes
________________

 - Caching keys refactoring
 - When brainiak is initialized, all cache is flushed
 - ``customize.py`` script allows uploading customizations to CMAaaS
 - Only expanded URIs will be used internally from now on
 - Nginx-related: comment out ``X-Scheme`` so that ``X-Forwarded-Proto`` works correctly to https


Version 2.3.8 - 2013/10/04
--------------------------

Fix
___

 - Suggest query using custom fields (before it wasn't working properly)

 - The CORS header 'Access-Control-Allow-Origin: *' was absent in error responses

 - Fix in error messages when context_name, class_name, instance_id received '_',
  now error messages render the contents of class_uri. graph_uri and instance_uri.


Version 2.3.7 - 2013/10/31
--------------------------

Enhacements
___________

 - General improvements on Suggest query (support unicode and partial queries)


Version 2.3.6 - 2013/10/28
--------------------------

Enhacements
___________

 - Remove xsd:string from instances when adding new instance

Version 2.3.3-2.3.5 - 2013/10/28
---------------------------------

Enhacements
___________

 - General log improvements


Version 2.3.2 - 2013/10/28
--------------------------

Enhacements
___________

 - General improvements on Suggest query


Version 2.3.1 - 2013/10/23
--------------------------

Enhacements
___________

 - Suggest works both with ElasticSearch 0.19.x and 0.90.x

Fixes
_____

 - Suggest supports queries ending and not ending in ``s`` (e.g. James)
 - During GET instances, if datatype is not defined in schema, return value as string and not as object (as before)


Version 2.3.0 - 2013/10/22
--------------------------

New features
____________

 - Retrieve (GET) and update (PUT) instances only by instance URI (see :doc:`/services/instance/instance`)

Refactorings
____________

 - Default to all resources is to use compressed URIs (``expand_uri=0``) in the response
 - Return 200 and empty items in listing resources (before it was 404)

Enhacements
___________

 - Enable caching to schema
 - Improved performace of suggest in 30x (subproperties are now cached at Redis)
 - Validate instance data during POST/PUT using its schema
 - Validate instance data during GET using its schema, to return values of properties as their types and cardinalities


Fixes
_____

 - Suggest query returns first exact match
 - Suggest query supports searches in values which include ``/``


Version 2.2.5 - 2013/10/15
-----------------------------------

New features
____________

 - Any class definition (returned by ``_schema``) now includes a new attribute for each predicate dictionary.
   The new attribute is ``class`` and it identifies the class uri in which this predicate was defined in the ontology.
   This serves to identify predicates that were inherited or direct declared in the class.


Refactor
________

 - #10645 Adding ``datatype`` property to the schema (class description), documenting
   precisely the semantic type of the range of a datatype predicate.
   The ``format`` field was used to convey that information, it is no longer used for this purpose.
 - #10694 Removing  parameters for optional URI expansion in responses: expand_uri_keys and expand_uri_values.
   We still support expand_uri to control expansion in the response, but it always impacts keys and values.

Fixes
_____

 - Adding unicode conversion to queries, that would break with special unicode chars.
 - ``graph`` property on any class definition was not expanded when parameter expand_uri was set to 1
 - Some predicates dictionaries in a class definition had inconsitencies when there was a clash between conflicting
   homonimous predicates defined in the same inheritance hierarchy.


Version 2.2.3 + 2.2.4 - 2013/09/25
-----------------------------------

New features
____________

 - Evolution of the  _suggest service, now supporting retrieval of instances referred by a given target predicate where a textual pattern occurs.
 - New expand_object_properties parameter used in instance retrieval.
 - New direct_instances_only parameter used in instance lists (collection retrieval).

Refactor
________

 - New endpoint was created for the isolated Braniak deploy.  api.semantica -> brainiak.semantica
 - Json-schema descriptions are now compliant with Draft-04, and no longer compliant with Draft-03
 - Removed the rdf:type property from the retrieved instance definition


Fixes
_____

 - During insertion of instance, property values now receive type cast.
   The mapping of json types to semantic types is still simplified. A precise mapping will be implemented in the future.
 - Removed the disk cache from Nginx.
 - Remove escaping of URL parameters for the profile directive (specifies the json-schema URL) in the Content-Type header.
 - Response body of backend erros appear in log files even if the log level is not set to DEBUG
 - Removal of restricted attributes (@ and _ prefixes) from the notification sent to the backstage bus


Version 2.2.0 + 2.2.2 - 2013/08/29
-----------------------------------

New features
____________

 - Suggest resource (see :doc:`/services/suggest/suggest`) with pagination (uses ElasticSearch)
 - Support to multiple triplestore endpoints (see :doc:`/troubleshoot` and X-Brainiak-Client-Id entry)

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
 - The versions 2.2.1 and 2.2.2 were mere adjustments in the deploy procedure with no new features


Version 2.1.0 - 2013/08/01
--------------------------

New features
____________

 - New parameters for optional URI expansion in responses: expand_uri, expand_uri_keys and expand_uri_values (see :doc:`services/instance/get_instance`).
 - Root schema now have direct hyperlinks to collection and instance (see :doc:`services/links`).
 - DOCs are now being deployed by default

Fixes
_____

 - Instances filter with PO ignores literals' type

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
