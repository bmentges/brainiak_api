from tornado.web import HTTPError

from brainiak import triplestore
from brainiak.utils.sparql import some_triples_deleted, is_result_empty


def delete_instance(query_params):
    dependants_result_dict = query_dependants(query_params)

    if not is_result_empty(dependants_result_dict):
        # TODO message with dependants URIs
        raise HTTPError(409, log_message="")

    query_result_dict = query_delete(query_params)

    if some_triples_deleted(query_result_dict, query_params['graph_uri']):
        return True


QUERY_DEPENDANTS_TEMPLATE = """
SELECT ?dependant {
  ?dependant ?predicate <%(instance_uri)s>
}
"""


def query_dependants(query_params):
    query = QUERY_DEPENDANTS_TEMPLATE % query_params
    result_dict = triplestore.query_sparql(query, query_params.triplestore_config)
    return result_dict


QUERY_DELETE_INSTANCE = """
DELETE FROM <%(graph_uri)s>
{ <%(instance_uri)s> ?p ?o }
WHERE
{ <%(instance_uri)s> ?p ?o }
"""


def query_delete(query_params):
    query = QUERY_DELETE_INSTANCE % query_params
    result_dict = triplestore.query_sparql(query, query_params.triplestore_config)
    return result_dict
