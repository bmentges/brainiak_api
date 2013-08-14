from tornado.web import HTTPError

from brainiak.utils.sparql import add_language_support, compress_keys_and_values, \
    filter_values
from brainiak import triplestore


def do_range_search(params):
    range_result = _get_predicate_ranges(params)

    classes = _validate_class_restriction(params, range_result)
    graphs = _validate_graph_restriction(params, range_result)

    compressed_result = compress_keys_and_values(range_result)
    return None


QUERY_PREDICATE_RANGES = """
SELECT DISTINCT ?range ?range_label ?range_graph {
  {
    <%(predicate)s> rdfs:range ?root_range .
  }
  UNION {
    <%(predicate)s> rdfs:range ?blank .
    ?blank a owl:Class .
    ?blank owl:unionOf ?enumeration .
    OPTIONAL { ?enumeration rdf:rest ?list_node OPTION(TRANSITIVE, t_min (0)) } .
    OPTIONAL { ?list_node rdf:first ?root_range } .
  }
  FILTER (!isBlank(?root_range))
  ?range rdfs:subClassOf ?root_range OPTION(TRANSITIVE, t_min (0)) .
  ?range rdfs:label ?range_label .
  GRAPH ?range_graph { ?range a owl:Class } .
  %(lang_filter_range_label)s
}
"""


def _build_predicate_ranges_query(query_params):
    (params, language_tag) = add_language_support(query_params, "range_label")
    return QUERY_PREDICATE_RANGES % params


def _get_predicate_ranges(params):
    query = _build_predicate_ranges_query(params)
    return triplestore.query_sparql(query, params.triplestore_config)


# call search_engine.py
def _get_search_results(params):
    pass


def _validate_class_restriction(params, range_result):
    classes = set(filter_values(range_result, "range"))
    if params["restrict_classes"] is not None:
        classes_not_in_range = list(set(params["restrict_classes"]).difference(classes))
        if classes_not_in_range:
            raise HTTPError(400,
                            "Classes {0} are not in the range of predicate '{1}'".format(classes_not_in_range, params["predicate"]))
        classes = params["restrict_classes"]

    return list(classes)


def _validate_graph_restriction(params, range_result):
    graphs = set(filter_values(range_result, "range_graph"))
    if params["restrict_graphs"] is not None:
        graphs_not_in_range = list(set(params["restrict_graphs"]).difference(graphs))
        if graphs_not_in_range:
            raise HTTPError(400,
                            "Classes in the range of predicate '{0}' are not in graphs {1}".format(graphs_not_in_range, params["predicate"]))
        graphs = params["restrict_graphs"]

    return list(graphs)


def _build_body_query(params):
    patterns = params["pattern"].lower().split()
    query_string = " AND ".join(patterns) + "*"
    body = {
        "query": {
            "query_string": {
                "query": query_string
            }
        }
    }

    return body
