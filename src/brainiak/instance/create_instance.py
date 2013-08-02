# -*- coding: utf-8 -*-
from tornado.web import HTTPError
from brainiak import triplestore
from brainiak.utils.sparql import create_explicit_triples, create_instance_uri, create_implicit_triples, \
    extract_instance_id, join_triples, join_prefixes, is_insert_response_successful


def create_instance(query_params, instance_data, instance_uri=None):
    class_uri = query_params["class_uri"]

    if not instance_uri:
        instance_uri = create_instance_uri(class_uri)

    triples = create_explicit_triples(instance_uri, instance_data)
    implicit_triples = create_implicit_triples(instance_uri, class_uri)
    triples.extend(implicit_triples)
    string_triples = join_triples(triples)

    prefixes = instance_data.get("@context", {})
    string_prefixes = join_prefixes(prefixes)
    response = query_create_instances(string_triples, string_prefixes, query_params["graph_uri"])
    if not is_insert_response_successful(response):
        raise HTTPError(500, log_message="Triplestore could not insert triples.")

    instance_id = extract_instance_id(instance_uri)
    return (instance_uri, instance_id)


QUERY_INSERT_TRIPLES = """
%(prefix)s
INSERT DATA INTO <%(graph_uri)s>
{
%(triples)s
}
"""


def query_create_instances(triples, prefix, graph_uri):
    query = QUERY_INSERT_TRIPLES % {"triples": triples, "prefix": prefix, "graph_uri": graph_uri}
    return triplestore.query_sparql(query, query_params.triplestore_config)
