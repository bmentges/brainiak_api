.. _parametrization:

Overriding URIs
===============

The conventional patterns for assembling the URIs associated with resources are:

    ============  ===================================================
     Resources               URI
    ============  ===================================================
     context       <URI_PREFIX><context_id>/
     collection    <URI_PREFIX><context_id>/<class_id>
     class         <URI_PREFIX><context_id>/<class_id>/_schema
     instance      <URI_PREFIX><context_id>/<class_id>/<instance_id>
    ============  ===================================================

These are described in :ref:`resource_url_convention`.
Specially for legacy systems, there are times when we need to override these.

The following parameters are supported by all services:

    ================= ============ =======================================
     Parameter           Resource            URI
    ================= ============ =======================================
     graph_uri           context       <graph_uri>
     graph_prefix        context       <graph_prefix><context_id>
     class_uri           class         <class_uri>
     class_prefix        class         <class_prefix><class_id>
     instance_uri        instance      <instance_uri>
     instance_prefix     instance      <instance_prefix><instance_id>
    ================= ============ =======================================

Notice that all prefixes should terminate with ``/``

.. _override_context:

Overriding the URI for the context
----------------------------------

The parameters ``graph_uri`` and ``graph_prefix`` can be used to define the URI for the context.
The parameter ``graph_uri`` completely defines the URI for the context, specifying a particular graph in the triplestore.
When specified, the ``context_id`` referred in the URL for the service is ignored.

The parameter  ``graph_prefix`` serves to override the global URI_PREFIX setting when composing the URI for the context.
When specified, the URI for context becomes "<graph_prefix><context_id>/" .


.. _override_schema:

Overriding the URI for the collection+class
----------------------------------------------------

The parameters ``class_uri`` and ``class_prefix`` can be used to define the URI for the collection+class.
The parameter ``class_uri`` completely defines the URI for the colelction+class.
When specified, the ``class_id`` referred in the URL for the service is ignored.

The parameter  ``class_prefix`` serves to override the pattern "<URI_PREFIX><context_id>/" when composing the URI for the context.
When specified, the URI for context becomes "<graph_prefix><class_id>/" .

CAUTION: these parameters ``do not specify`` the graph where this class was defined, the latter follows the rules in :ref:`override_context`.


Overriding the URI for the instance
-----------------------------------

The parameters ``instance_uri`` and ``instance_prefix`` can be used to define the URI for the instance.
The parameter ``instance_uri`` completely defines the URI for the instance.
When specified, the ``instance_id`` referred in the URL for the service is ignored.

The parameter  ``instance_prefix`` serves to override the pattern "<URI_PREFIX><context_id>/<class_id>/" when composing the URI for the instance.
When specified, the URI for context becomes "<instance_prefix><instance_id>/" .

CAUTION: these parameters ``do not specify`` neither the graph nor the class URIs, those follow the rules in :ref:`override_context` and :ref:`override_schema` respectively.
