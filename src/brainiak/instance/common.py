from tornado.web import HTTPError
from brainiak import triplestore

QUERY_GET_CLASS_AND_GRAPH = u"""
SELECT DISTINCT ?class_uri ?graph_uri {
    GRAPH ?graph_uri { <%(instance_uri)s> a ?class_uri . }
}
"""


def get_class_and_graph(query_params):
    query = QUERY_GET_CLASS_AND_GRAPH % query_params
    return triplestore.query_sparql(query, query_params.triplestore_config)


def must_retrieve_graph_and_class_uri(query_params):
    try:
        values = [query_params["class_name"], query_params["instance_id"], query_params["graph_uri"]]
        query_params["instance_uri"]
    except KeyError as ex:
        raise HTTPError(404, log_message=u"Parameter <{0:s}> is missing in order to update instance.".format(ex))
    return all([value == u"_" for value in values])


def extract_class_uri(bindings):
    try:
        class_uri = bindings[0]['class_uri']['value']
    except IndexError:
        return None
    [item.pop('class_uri') for item in bindings]
    return class_uri


def extract_graph_uri(bindings):
    try:
        graph_uri = bindings[0]['graph_uri']['value']
    except IndexError:
        return None
    [item.pop('graph_uri') for item in bindings]
    return graph_uri
