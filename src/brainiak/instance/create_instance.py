# -*- coding: utf-8 -*-
from tornado.web import HTTPError
from brainiak import triplestore
from brainiak.schema.get_class import get_cached_schema
from brainiak.utils.i18n import _
from brainiak.utils.sparql import create_explicit_triples, create_instance_uri, create_implicit_triples, \
    extract_instance_id, join_triples, join_prefixes, is_insert_response_successful, InstanceError,\
    are_there_label_properties_in


def create_instance(query_params, instance_data, instance_uri=None):
    class_uri = query_params["class_uri"]
    graph_uri = query_params["graph_uri"]

    if not are_there_label_properties_in(instance_data):
        raise HTTPError(400, log_message=_(u"Label properties like rdfs:label or its subproperties are required"))

    if not instance_uri:
        instance_uri = create_instance_uri(class_uri)

    class_object = get_cached_schema(query_params)

    try:
        triples = create_explicit_triples(instance_uri, instance_data, class_object, graph_uri, query_params)
    except InstanceError, exception:
        raise HTTPError(400, log_message=exception.message)

    implicit_triples = create_implicit_triples(instance_uri, class_uri)
    triples.extend(implicit_triples)
    string_triples = join_triples(triples)

    prefixes = instance_data.get("@context", {})
    string_prefixes = join_prefixes(prefixes)
    query_params.update({"triples": string_triples, "prefix": string_prefixes})

    response = query_create_instances(query_params)
    if not is_insert_response_successful(response):
        raise HTTPError(500, log_message=_("Triplestore could not insert triples."))

    instance_id = extract_instance_id(instance_uri)
    return (instance_uri, instance_id)


QUERY_INSERT_TRIPLES = u"""
%(prefix)s
INSERT DATA INTO <%(graph_uri)s>
{
%(triples)s
}
"""


def query_create_instances(query_params):
    query = QUERY_INSERT_TRIPLES % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)
