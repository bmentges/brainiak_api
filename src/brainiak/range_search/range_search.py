from tornado.web import HTTPError

from brainiak import settings, triplestore
from brainiak.search_engine import run_search
from brainiak.utils.sparql import add_language_support, compress_keys_and_values, filter_values, is_result_empty
from brainiak.utils.resources import calculate_offset, decorate_dict_with_pagination

SUGGEST_REQUIRED_PARAMS = ('pattern', 'predicate')
SUGGEST_OPTIONAL_PARAMS = ('search_fields', 'search_classes', 'search_graphs')
RDFS_LABEL = "http://www.w3.org/2000/01/rdf-schema#label"


def do_range_search(params):
    range_result = _get_predicate_ranges(params)
    if is_result_empty(range_result):
        raise HTTPError(400, "Either the predicate {0} does not exists or it does not have any rdfs:range defined in the triplestore".format(params['predicate']))

    classes = _validate_class_restriction(params, range_result)
    graphs = _validate_graph_restriction(params, range_result)
    indexes = [_graph_uri_to_index_name(graph) for graph in graphs]

    compressed_result = compress_keys_and_values(range_result)
    class_label_dict = _build_class_label_dict(compressed_result)

    title_fields = [RDFS_LABEL]
    title_fields += _get_subproperties(params, RDFS_LABEL)
    search_fields = list(set(_get_search_fields(params) + title_fields))

    request_body = _build_body_query(params, classes, search_fields)
    elasticsearch_result = run_search(request_body, indexes=indexes)

    items, item_count = _build_items(elasticsearch_result, class_label_dict, title_fields)

    if not items:
        return None
    else:
        return build_json(items, item_count, params)


def build_json(items_list, item_count, query_params):

    json = {
        '_base_url': query_params.base_url,
        'items': items_list,
        "@context": {"@language": query_params.get("lang")},
    }

    decorate_dict_with_pagination(json, query_params, item_count)

    return json


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


QUERY_SUBPROPERTIES = """
DEFINE input:inference <http://semantica.globo.com/ruleset>
SELECT DISTINCT ?property WHERE {
  ?property rdfs:subPropertyOf <%s>
}
"""


def _get_subproperties(params, super_property):
    query = QUERY_SUBPROPERTIES % super_property
    result = triplestore.query_sparql(query, params.triplestore_config)
    return filter_values(result, "property")


def _get_search_fields(params):
    search_fields_in_params = params.get("search_fields", [])
    search_fields = set(search_fields_in_params)
    for field in search_fields_in_params:
        sub_properties = _get_subproperties(params, field)
        search_fields.update(sub_properties)

    return list(search_fields)


def _validate_class_restriction(params, range_result):
    classes = set(filter_values(range_result, "range"))
    if "search_classes" in params:
        classes_not_in_range = list(set(params["search_classes"]).difference(classes))
        if classes_not_in_range:
            raise HTTPError(400,
                            "Classes {0} are not in the range of predicate '{1}'".format(classes_not_in_range, params["predicate"]))
        classes = params["search_classes"]

    return list(classes)


def _validate_graph_restriction(params, range_result):
    graphs = set(filter_values(range_result, "range_graph"))
    if "search_graphs" in params:
        graphs_set = set(params["search_graphs"])
        graphs_not_in_range = list(graphs_set.difference(graphs))
        if graphs_not_in_range:
            raise HTTPError(400,
                            "Classes in the range of predicate '{0}' are not in graphs {1}".format(params["predicate"], graphs_not_in_range))
        graphs = graphs_set

    graphs = graphs.difference(set(settings.GRAPHS_WITHOUT_INSTANCES))

    if not graphs:
        raise HTTPError(400,
                        "Classes in the range of predicate '{0}' are in graphs without instances, such as: {1}".format(
                            params["predicate"], settings.GRAPHS_WITHOUT_INSTANCES))
    return list(graphs)


def _build_body_query(params, classes, search_fields):
    patterns = params["pattern"].lower().split()
    query_string = " AND ".join(patterns) + "*"
    return_fields = search_fields  # TODO return_fields in params
    body = {
        "from": int(calculate_offset(params)),
        "size": int(params.get("per_page", settings.DEFAULT_PER_PAGE)),
        "fields": return_fields,
        "query": {
            "query_string": {
                "query": query_string,
                "fields": search_fields
            }
        },
        "filter": _build_type_filters(classes)
    }

    return body


def _build_type_filters(classes):
    filter_list = []
    for klass in classes:
        filter_dict = {"type": {"value": klass}}
        filter_list.append(filter_dict)

    type_filters = {
        "or": filter_list
    }
    return type_filters


def _build_class_label_dict(compressed_result):
    class_label_dict = {}
    for result in compressed_result:
        class_label_dict[result["range"]] = result["range_label"]
    return class_label_dict


def _get_title_value(elasticsearch_fields, title_fields):
    for field in reversed(title_fields):
        title = elasticsearch_fields.get(field)
        if title:
            return title
    raise RuntimeError("No title fields in search engine")


def _build_items(result, class_label_dict, title_fields):
    items = []
    item_count = result["hits"]["total"]
    if item_count:
        for item in result["hits"]["hits"]:
            item_dict = {
                "title": _get_title_value(item["fields"], title_fields),
                "@id": item["_id"],
                "@type": item["_type"],
                "type_title": class_label_dict[item["_type"]]
            }
            # return other fields only when return_fields is specified
            # item_dict.update(item["fields"])
            items.append(item_dict)

    return items, item_count

GRAPH_PREFIX = "http://semantica.globo.com/"


def _graph_uri_to_index_name(graph_uri):
    if graph_uri == GRAPH_PREFIX:
        return "semantica.glb"
    else:
        # http://semantica.globo.com/place/ > semantica.place
        return "semantica." + graph_uri.split("/")[-2]
