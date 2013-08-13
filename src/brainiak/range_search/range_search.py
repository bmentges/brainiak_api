from brainiak.utils.sparql import add_language_support
from brainiak import triplestore


def do_range_search(params):
    pass


QUERY_PREDICATE_RANGES = """
SELECT DISTINCT ?range ?label_range {
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
  ?range rdfs:label ?label_range .
  %(lang_filter_label_range)s
}
"""


def _build_predicate_ranges_query(query_params):
    (params, language_tag) = add_language_support(query_params, "label_range")
    return QUERY_PREDICATE_RANGES % params


def _get_predicate_ranges(params):
    query = _build_predicate_ranges_query(params)
    return triplestore.query_sparql(query, params.triplestore_config)


def _get_search_results(params):
    pass


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
