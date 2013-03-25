from tornado.web import HTTPError

from brainiak import triplestore
from brainiak.utils.sparql import is_result_true


def edit_instance(query_params):
    if not instance_exists(query_params):
        raise HTTPError(404, log_message="Instance <{0}> does not exist".format(query_params["instance_uri"]))

    query_edit_instance(query_params)


MODIFY_QUERY = u"""
MODIFY GRAPH <%(graph_uri)s>
DELETE
{ <%(instance_uri)s> ?predicate ?old_value }
%(insert_triples)s
WHERE
{ <%(instance_uri)s> ?predicate ?old_value }
"""


def query_edit_instance(query_params):
    pass

QUERY_INSTANCE_EXISTS_TEMPLATE = """
ASK {<%(instance_uri)s> ?p ?o}
"""


def instance_exists(query_params):
    query = QUERY_INSTANCE_EXISTS_TEMPLATE % query_params
    result_dict = triplestore.query_sparql(query)
    return is_result_true(result_dict)
