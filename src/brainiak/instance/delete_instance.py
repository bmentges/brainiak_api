from tornado.web import HTTPError
from brainiak import triplestore
from brainiak.utils.sparql import some_triples_deleted, is_result_empty


def delete_instance(query_params):
    graph_uri = query_params['graph_uri']
    instance_uri = query_params['instance_uri']

    dependants_result_dict = query_dependants(instance_uri)

    if not is_result_empty(dependants_result_dict):
        # TODO message with dependants URIs
        raise HTTPError(409, log_message="")

    query_result_dict = query_delete(graph_uri, instance_uri)

    if some_triples_deleted(query_result_dict, graph_uri):
        return True


QUERY_DEPENDANTS_TEMPLATE = """
SELECT ?dependant {
  ?dependant ?predicate <%(instance_uri)s>
}
"""


def query_dependants(instance_uri):
    query = QUERY_DEPENDANTS_TEMPLATE % {
        "instance_uri": instance_uri
    }
    result_dict = triplestore.query_sparql(query, query_params.triplestore_config)
    return result_dict


QUERY_DELETE_INSTANCE = """
DELETE FROM <%(graph_uri)s>
{ <%(instance_uri)s> ?p ?o }
WHERE
{ <%(instance_uri)s> ?p ?o }
"""


def query_delete(graph_uri, instance_uri):
    query = QUERY_DELETE_INSTANCE % {
        "graph_uri": graph_uri,
        "instance_uri": instance_uri
    }
    result_dict = triplestore.query_sparql(query, query_params.triplestore_config)
    return result_dict
